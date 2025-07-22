"""
Arachne Config Downloader
"""

import importlib.resources
import sys
import os
import datetime
import time
import json
import socket
import stat
import threading

import netaddr
import requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL

import dbus
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QDialog
    )
from PyQt6.QtGui import (
    QIcon,
    QDesktopServices
    )
from PyQt6.QtCore import (
    QDir,
    QUrl,
    QFile
    )

import pyarachnecdl.data
from .settings_dialog import SettingsDialog
from .settings import Settings, DownloadType, TimeUnit
from . import network_manager_connection
from .network_manager_connection import ConnectionType

USER_CONFIG_API_PATH = "/api/openvpn/user_config"

class ArachneConfigDownloader(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setOrganizationName("Claas Nieslony")
        self.setOrganizationDomain("nieslony.at")
        self.setApplicationName("Arachne Config Downloader")
        self.setDesktopFileName("arachne-cdl")
        self.setQuitOnLastWindowClosed(False)

        self._ca_file_name = ""
        self._cert_file_name = ""
        self._key_file_name = ""

        self.settings = Settings()
        self.settings.sync()

        self.icon_blue = QIcon(
            str(importlib.resources.files(pyarachnecdl.data) / "arachne-blue.svg")
            )
        self.icon_green = QIcon(
            str(importlib.resources.files(pyarachnecdl.data) / "arachne-green.svg")
            )
        self.icon_red = QIcon(
            str(importlib.resources.files(pyarachnecdl.data) / "arachne-red.svg")
            )
        self.icon_yellow = QIcon(
            str(importlib.resources.files(pyarachnecdl.data) / "arachne-yellow.svg")
            )
        self.icon_pixmap = self.icon_green.pixmap(16, 16)

        self._create_system_tray()

        if self.settings.auto_download:
            if self.settings.download_delay_unit == TimeUnit.SEC:
                delay = self.settings.download_delay
            elif self.settings.download_delay_unit == TimeUnit.MIN:
                delay = self.settings.download_delay * 60
            elif self.settings.download_delay_unit == TimeUnit.HOUR:
                delay = self.settings.download_delay * 60 * 60
            else:
                return
            self.download_thread = threading.Timer(delay, self._scheduled_download)
            self.download_thread.start()

    def _update_status(self):
        last_successful_download = self.settings.last_successful_download
        dt = datetime.datetime.fromtimestamp(last_successful_download)
        now = time.time()

        if last_successful_download == -1:
            self.tray_icon.setIcon(self.icon_blue)
            self.tray_icon.setToolTip(
                f"{self.applicationName()}\nConfiguration has nevew been downloaded"
                )
        elif now - last_successful_download < 7 * 24 * 60 * 60:
            self.tray_icon.setIcon(self.icon_green)
            self.tray_icon.setToolTip(
                f"{self.applicationName()}\nLast configuration update: {dt.ctime()}"
                )
        elif now - last_successful_download < 31 * 24 * 60 * 60:
            self.tray_icon.setIcon(self.icon_yellow)
            self.tray_icon.setToolTip(
                f"{self.applicationName()}\nError: Last configuration update more than 7 days ago: {dt.ctime()}"
                )
        else:
            self.tray_icon.setIcon(self.icon_red)
            self.tray_icon.setToolTip(
                f"{self.applicationName()}\nError: Last configuration update more than 31 days ago: {dt.ctime()}"
                )

    def _is_nm_connection_allowed(self) -> bool:
        allowed_cons = self.settings.allowed_connections
        for con in network_manager_connection.get_all_active():
            if con.uuid in allowed_cons:
                return True
            if con.con_type == ConnectionType.WIFI and self.settings.allow_download_from_wifi:
                return True
            if con.con_type == ConnectionType.WIRED and self.settings.allow_download_from_wired:
                return True
            if con.con_type == ConnectionType.VPN and \
               con.uuid == self.settings.connection_uuid and \
               self.settings.allow_download_from_vpn:
                return True

        return False


    def _create_system_tray(self):
        self.menu = QMenu(None)
        self.menu.addAction("Download now", self._on_download_now)
        self.menu.addAction("Settings...", self._on_settings)
        self.menu.addAction("Open Arachne in Webbrowser", self._on_open_arachne_configuration)
        self.menu.addSeparator()
        self.menu.addAction("About Qt..", self.aboutQt)
        self.menu.addAction("Exit", self._on_exit)

        self.tray_icon = QSystemTrayIcon(None)
        self._update_status()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

    def _error(self, msg):
        self.tray_icon.showMessage("Error", msg, QSystemTrayIcon.MessageIcon.Warning)

    def _info(self, msg):
        self.tray_icon.showMessage("Info", msg, QSystemTrayIcon.MessageIcon.Information)

    def _scheduled_download(self):
        if self._is_nm_connection_allowed():
            self._on_download_now(False)
        if self.settings.auto_download:
            if self.settings.download_interval_unit == TimeUnit.SEC:
                delay = self.settings.download_interval
            elif self.settings.download_interval_unit == TimeUnit.MIN:
                delay = self.settings.download_interval * 60
            elif self.settings.download_interval_unit == TimeUnit.HOUR:
                delay = self.settings.download_interval * 60 * 60
            else:
                return

            self.download_thread = threading.Timer(delay, self._scheduled_download)
            self.download_thread.start()

    def _save_file(self, content, show_info):
        config_dir = self.settings.download_destination.replace("~/", QDir.homePath() + "/")
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
        fn = config_dir + "/OpenVPN_arachne.conf"
        f = QFile(fn)
        try:
            with open(QFile.OpenModeFlag.WriteOnly, encoding="utf-8") as f:
                f.write(content)
                f.close()
                if show_info:
                    self._info(f"Configuration saved as {fn}")
        except IOError as ex:
            if show_info:
                self._error(f"Cannot save {fn}: {str(ex)}")

    def _update_networkmaneger_connection(self, con_data, show_info):
        bus = dbus.SystemBus()
        settings = bus.get_object(
            "org.freedesktop.NetworkManager",
            "/org/freedesktop/NetworkManager/Settings"
            )
        con_settings = {
            "connection": {
                "id": con_data["name"],
                "type": "vpn",
                "autoconnect": False,
                "permissions": ["user:" + os.getlogin()]
                },
            "vpn": {
                "service-type": "org.freedesktop.NetworkManager.openvpn",
                "data": {
                    "ca": self._ca_file_name,
                    "cert": self._cert_file_name,
                    "key": self._key_file_name
                    } | { k: str(v) for k,v in con_data["data"].items() }
                },
            "ipv4": {
                "never-default": con_data["ipv4"]["never-default"],
                "method": "auto",
                "dns-search": con_data["ipv4"]["dns-search"],
                "dns": [
                    dbus.types.UInt32(
                        socket.htonl(netaddr.IPAddress(ip).value)
                    )
                    for ip in con_data["ipv4"]["dns"]
                    ]
                }
            }

        try:
            cur_obj_path = settings.GetConnectionByUuid(
                self.settings.connection_uuid,
                dbus_interface="org.freedesktop.NetworkManager.Settings"
                )
            cur_con = bus.get_object("org.freedesktop.NetworkManager", cur_obj_path)
            cur_con.Update(
                con_settings,
                dbus_interface="org.freedesktop.NetworkManager.Settings.Connection"
                )
            if show_info:
                self._info(f"Updaded connection '{con_data['name']}'")
        except dbus.exceptions.DBusException:
            new_con_obj_path = settings.AddConnection(
                con_settings,
                dbus_interface="org.freedesktop.NetworkManager.Settings"
            )
            new_con = bus.get_object("org.freedesktop.NetworkManager", new_con_obj_path)
            new_settings = new_con.GetSettings(
                dbus_interface="org.freedesktop.NetworkManager.Settings.Connection"
                )
            uuid = new_settings["connection"]["uuid"]
            self.settings.connection_uuid = uuid
            if show_info:
                self._info(f"Added new connection '{con_data['name']}' with uuid ''{uuid}'")

    def _save_certs(self, json_data):
        home = QDir.home()
        home.mkdir(".cert")
        if "caCertFilename" in json_data["certificates"]:
            self._ca_file_name = f"{home.absolutePath()}/.cert/{json_data['certificates']['caCertFilename']}"
        else:
            self._ca_file_name = f"{home.absolutePath()}/.cert/arachne-ca.crt"
        if "userCertFilename" in json_data["certificates"]:
            self._cert_file_name = f"{home.absolutePath()}/.cert/{json_data['certificates']['userCertFilename']}"
        else:
            self._cert_file_name = f"{home.absolutePath()}/.cert/arachne-cert.crt"
        if "privateKeyFilename" in json_data["certificates"]:
            self._key_file_name = f"{home.absolutePath()}/.cert/{json_data['certificates']['privateKeyFilename']}"
        else:
            self._key_file_name = f"{home.absolutePath()}/.cert/arachne-cert.key"

        with open(self._ca_file_name,  "w", encoding="utf-8") as f:
            f.write(json_data["certificates"]["caCert"])
            f.close()
        with open(self._cert_file_name, "w", encoding="utf-8") as f:
            f.write(json_data["certificates"]["userCert"])
            f.close()
        with open(self._key_file_name, "w", encoding="utf-8") as f:
            f.write(json_data["certificates"]["privateKey"])
            f.close()
        os.chmod(self._key_file_name, stat.S_IRUSR | stat.S_IWUSR)

    def _on_download_now(self, show_info=True):
        url = self.settings.admin_server_url + USER_CONFIG_API_PATH
        if self.settings.download_type == DownloadType.NETWORK_MANAGER:
            url += "?format=json"
        try:
            r = requests.get(
                url,
                auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL),
                timeout=6,
                verify=(not self.settings.ignore_ssl_errors)
                )
            r.raise_for_status()
            if self.settings.download_type == DownloadType.NETWORK_MANAGER:
                json_data = r.json()
                self._save_certs(json_data)
                self._update_networkmaneger_connection(json_data, show_info)
            elif self.settings.download_type == DownloadType.OVPN:
                self._save_file(r.content, show_info)
            self.settings.touch_last_successful_download()
        except json.decoder.JSONDecodeError as ex:
            if show_info:
                self._error(f"Error parsing json: {str(ex)}")
        except requests.exceptions.RequestException as ex:
            if show_info:
                self._error(f"Cannot download configuration from {url}: {str(ex)}")
        self._update_status()

    def _on_settings(self):
        dlg = SettingsDialog(QIcon(self.icon_pixmap))
        dlg.load_settings(self.settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.save_settings(self.settings)
            self.settings.sync()

    def _on_open_arachne_configuration(self):
        QDesktopServices.openUrl(QUrl(self.settings.admin_server_url))

    def _on_exit(self):
        self.download_thread.cancel()
        self.quit()

def main():
    app = ArachneConfigDownloader()
    sys.exit(app.exec())
