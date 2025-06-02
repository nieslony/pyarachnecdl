from enum import StrEnum
import socket

from PyQt6.QtCore import QSettings

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
    def allow_download_all_wifi(self) -> bool:
        return bool(self.value("allowDownloadAllWifi", True))

    @allow_download_all_wifi.setter
    def allow_download_all_wifi(self, allow: bool):
        self.setValue("allowDownloadAllWifi", allow)

    @property
    def allow_download_all_wired(self) -> bool:
        return bool(self.value("allowDownloadAllWired", True))

    @allow_download_all_wired.setter
    def allow_download_all_wired(self, allow: bool):
        self.setValue(allow)

    @property
    def allow_download_from_vpn(self) -> bool:
        return bool(self.value("allowDownloadFromVpn", True))

    @allow_download_from_vpn.setter
    def allow_download_from_vpn(self, allow: bool):
        self.setValue("allow_download_from_vpn", allow)

    @property
    def auto_download(self) -> bool:
        return bool(self.value("autoDownload", True))

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
            print("Found interval number: " + str(v) + " = " + list(TimeUnit)[v])
        except ValueError:
            pass
        if isinstance(v, str):
            print("Found interval str: " + v)
            return TimeUnit[v]
        if isinstance(v, int):
            return list(TimeUnit)[v]

        return None

    @download_interval_unit.setter
    def download_interval_unit(self, unit: TimeUnit):
        print("Setter: " + str(unit))
        self.value("downloadIntervalUnit", unit.name)
        print("Set: " + str(self.download_interval_unit))

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
        return bool(self.value("ignoreSslErrors", False))

    @ignore_ssl_errors.setter
    def ignore_ssl_errors(self, ignore: bool):
        self.setValue("ignoreSslErrors", ignore)

    @property
    def last_successful_download(self) -> int:
        return int(self.value("lastSuccesfulDownload", -1))

    @last_successful_download.setter
    def last_successful_download(self, last_dl: int):
        self.value("lastSuccesfulDownload", last_dl)

    def __str__(self) -> str:
        l = []
        for k in self.allKeys():
            l.append(k + "=" + str(self.value(k)))
        return str(l)
