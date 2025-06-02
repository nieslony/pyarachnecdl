"""
Arachne Config Downloader
"""

import sys
import os
import time
import dbus
import json
import ipaddress
import threading
import requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QDialog
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtCore import QUrl, QFile, QDir, QTimer

from .settings_dialog import SettingsDialog
from .settings import Settings, DownloadType, TimeUnit

USER_CONFIG_API_PATH = "/api/openvpn/user_config"

class ArachneConfigDownloader(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setOrganizationName("Claas Nieslony")
        self.setOrganizationDomain("nieslony.at")
        self.setApplicationName("Arachne Config Downloader")
        self.setDesktopFileName("arachne-cdl")

        self.setQuitOnLastWindowClosed(False)
        self._create_system_tray()

        self.settings = Settings()
        self.settings.sync()
        print(str(self.settings))

        if self.settings.auto_download:
            if self.settings.download_delay_unit == TimeUnit.SEC:
                delay = self.settings.download_delay
            elif self.settings.download_delay_unit == TimeUnit.MIN:
                delay = self.settings.download_delay * 60
            elif self.settings.download_delay_unit == TimeUnit.HOUR:
                delay = self.settings.download_delay * 60 * 60
            self.download_thread = threading.Timer(delay, self._scheduled_download)
            self.download_thread.start()

    def _create_system_tray(self):
        self.menu = QMenu(None)
        self.menu.addAction("Download now", self._on_download_now)
        self.menu.addAction("Settings...", self._on_settings)
        self.menu.addAction("Open Arachne in Webbrowser", self._on_open_arachne_configuration)
        self.menu.addSeparator()
        self.menu.addAction("Exit", self._on_exit)

        self.tray_icon = QSystemTrayIcon(QIcon(""), None)
        self.tray_icon.setToolTip("Arachne Config Downloader")
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

    def _error(self, msg):
        print(f"{time.asctime()}: {msg}")

    def _info(self, msg):
        print(f"{time.asctime()}: {msg}")

    def _scheduled_download(self):
        self._on_download_now()
        if self.settings.auto_download:
            if self.settings.download_interval_unit == TimeUnit.SEC:
                delay = self.settings.download_interval
            elif self.settings.download_interval_unit == TimeUnit.MIN:
                delay = self.settings.download_interval * 60
            elif self.settings.download_interval_unit == TimeUnit.HOUR:
                delay = self.settings.download_interval * 60 * 60
            self.download_thread = threading.Timer(delay, self._scheduled_download)
            self.download_thread.start()

    def _save_file(self, content):
        dir = self.settings.download_destination.replace("~/", QDir.homePath() + "/")
        if not os.path.exists(dir):
            os.mkdir(dir)
        fn = dir + "/OpenVPN_arachne.conf"
        f = QFile(fn)
        f.open(QFile.OpenModeFlag.WriteOnly)
        f.write(content)
        f.close()

    def _update_networkmaneger_connection(self, content):
        try:
            con_data = json.loads(content)
        except json.decoder.JSONDecodeError as ex:
            self._error(str(ex))
            return
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
                    "ca": "ca.crt",
                    "cert": "cert.crt",
                    "key": "key.key"
                    } | dict([ (k,str(v)) for k,v in con_data["data"].items() ])
                },
            "ipv4": {
                "never-default": con_data["ipv4"]["never-default"],
                "method": "auto",
                "dns-search": con_data["ipv4"]["dns-search"],
                "dns": [
                    dbus.types.UInt32(ipaddress.ip_address(ip)) for ip in con_data["ipv4"]["dns"]
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
            self._info(f"Updaded connection '{con_data['name']}' with uuid '{self.settings.connection_uuid}' at {cur_obj_path}")
        except dbus.exceptions.DBusException as ex:
            new_con_obj_path = settings.AddConnection(
                con_settings,
                dbus_interface="org.freedesktop.NetworkManager.Settings"
            )
            new_con = bus.get_object("org.freedesktop.NetworkManager", new_con_obj_path)
            new_settings = new_con.GetSettings(dbus_interface="org.freedesktop.NetworkManager.Settings.Connection")
            uuid = new_settings["connection"]["uuid"]
            self.settings.connection_uuid = uuid
            self._info(f"Added new connection '{con_data['name']}' with uuid ''{uuid}'")

    def _on_download_now(self):
        url = self.settings.admin_server_url + USER_CONFIG_API_PATH
        if (self.settings.download_type == DownloadType.NETWORK_MANAGER):
            url += "?format=json"
        try:
            r = requests.get(url, auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL))
        except requests.exceptions.ConnectionError as ex:
            self._error(f"Cannot connect to {url}: {str(ex)}")
            return

        if r.status_code == 401:
            print("Denied")
            return
        if r.status_code != 200:
            print("Error " + str(r.status_code))
            return

        if self.settings.download_type == DownloadType.NETWORK_MANAGER:
            self._update_networkmaneger_connection(r.content)
        elif self.settings.download_type == DownloadType.OVPN:
            self._save_file(r.content)

    def _on_settings(self):
        dlg = SettingsDialog()
        dlg.load_settings(self.settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.save_settings(self.settings)
            print(self.settings)
            self.settings.sync()

    def _on_open_arachne_configuration(self):
        QDesktopServices.openUrl(QUrl(self.settings.admin_server_url))

    def _on_exit(self):
        self._info("Killing timer")
        self.download_thread.cancel()
        self._info("Timer killed")
        self.quit()

def main():
    app = ArachneConfigDownloader()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
