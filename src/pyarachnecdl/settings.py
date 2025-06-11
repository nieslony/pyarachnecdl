from enum import StrEnum
import socket
import ast
import time

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

class DownloadType(StrEnum):
    """
    Downlod Type
    """
    NETWORK_MANAGER = "Network Manager Configuration"
    OVPN = ".ovpn File"

class TimeUnit(StrEnum):
    """
    Time Unit
    """
    SEC = "Seconds"
    MIN = "Minutes"
    HOUR = "Hours"

class Settings(QSettings):
    """
    Settings Dialog
    """
    def __init__(self):
        app = QApplication.instance()
        org_name = app.organizationName().replace(" ", "")
        app_name = app.applicationName().replace(" ", "")
        super().__init__(org_name, app_name)

    @property
    def admin_server_url(self) -> str:
        return self.value(
            "adminServerurl",
            "https://arachne." + ".".join(socket.gethostname().split(".")[1:]) + "/arachne"
            )

    @admin_server_url.setter
    def admin_server_url(self, url: str):
        self.setValue("adminServerurl", url)

    @property
    def auto_download(self) -> bool:
        return self.value("autoDownload", True, type=bool)

    @auto_download.setter
    def auto_download(self, auto_dl: bool):
        self.setValue("autoDownload", auto_dl)

    @property
    def connection_uuid(self) -> str:
        return self.value("connectionUuid", "")

    @connection_uuid.setter
    def connection_uuid(self, uuid: str):
        self.setValue("connectionUuid", uuid)

    @property
    def download_delay(self) -> int:
        return int(self.value("downloadDelay", 5))

    @download_delay.setter
    def download_delay(self, delay: int):
        self.setValue("downloadDelay", delay)

    @property
    def download_delay_unit(self) -> TimeUnit:
        v = self.value("downloadDelayUnit", TimeUnit.MIN.name)
        try:
            v = int(v)
        except ValueError:
            pass
        if isinstance(v, str):
            return TimeUnit[v]
        if isinstance(v, int):
            return list(TimeUnit)[v]

        return None

    @download_delay_unit.setter
    def download_delay_unit(self, unit: TimeUnit):
        self.setValue("downloadDelayUnit", unit.name)

    @property
    def download_destination(self) -> str:
        return self.value("downloadDestination")

    @download_destination.setter
    def download_destination(self, destination: str):
        self.setValue("downloadDestination", destination)

    @property
    def download_interval(self) -> int:
        return int(self.value("downloadInterval", 60))

    @download_interval.setter
    def download_interval(self, interval: int):
        self.setValue("downloadInterval", interval)

    @property
    def download_interval_unit(self) -> TimeUnit:
        v = self.value("downloadIntervalUnit", TimeUnit.MIN.name)
        try:
            v = int(v)
        except ValueError:
            pass
        if isinstance(v, str):
            return TimeUnit[v]
        if isinstance(v, int):
            return list(TimeUnit)[v]

        return None

    @download_interval_unit.setter
    def download_interval_unit(self, unit: TimeUnit):
        self.setValue("downloadIntervalUnit", unit.name)

    @property
    def download_type(self) -> DownloadType:
        v = self.value("downloadType", DownloadType.NETWORK_MANAGER.name)
        try:
            v = int(v)
        except ValueError:
            pass
        if isinstance(v, str):
            return DownloadType[v]
        if isinstance(v, int):
            return list(DownloadType)[v]

        return None

    @download_type.setter
    def download_type(self, dl_type: DownloadType):
        self.setValue("downloadType", dl_type.name)

    @property
    def ignore_ssl_errors(self) -> bool:
        return self.value("ignoreSslErrors", False, type=bool)

    @ignore_ssl_errors.setter
    def ignore_ssl_errors(self, ignore: bool):
        self.setValue("ignoreSslErrors", ignore)

    @property
    def last_successful_download(self) -> int:
        return int(self.value("lastSuccesfulDownload", -1))

    @last_successful_download.setter
    def last_successful_download(self, last_dl: int):
        self.setValue("lastSuccesfulDownload", last_dl)

    @property
    def allow_download_from_wifi(self) -> bool:
        return self.value("allowDownloadFromWifi", True, type=bool)

    @allow_download_from_wifi.setter
    def allow_download_from_wifi(self, allow: bool):
        self.setValue("allowDownloadFromWifi", allow)

    @property
    def allow_download_from_wired(self) -> bool:
        return self.value("allowDownloadFromWired", True, type=bool)

    @allow_download_from_wired.setter
    def allow_download_from_wired(self, allow: bool):
        self.setValue("allowDownloadFromWired", allow)

    @property
    def allow_download_from_vpn(self) -> bool:
        return self.value("allowDownloadFromVpn", True, type=bool)

    @allow_download_from_vpn.setter
    def allow_download_from_vpn(self, allow: bool):
        self.setValue("allowDownloadFromVpn", allow)

    @property
    def allowed_connections(self) -> list:
        return ast.literal_eval(self.value("allowedConnections", "[]"))

    @allowed_connections.setter
    def allowed_connections(self, cons: list):
        self.setValue("allowedConnections", str(cons))

    def touch_last_successful_download(self):
        now = int(time.time())
        self.last_successful_download = now

    def __str__(self) -> str:
        l = []
        for k in self.allKeys():
            l.append(k + "=" + str(self.value(k)))
        return str(l)
