import dbus
from enum import StrEnum, auto

class ConnectionType(StrEnum):
    WIRED = "802-3-ethernet"
    WIFI = "802-11-wireless"
    VPN = "vpn"
    OTHER = auto()

class NetworkManagerConnection:
    def __init__(self, con_type, con_name, con_uuid):
        self.con_type = con_type
        self.name = con_name
        self.uuid = con_uuid

    def __str__(self) -> str:
        return f"type={self.con_type} name={self.name} uuid={self.uuid}"

def get_all() -> list:
    bus = dbus.SystemBus()
    settings = bus.get_object(
        "org.freedesktop.NetworkManager",
        "/org/freedesktop/NetworkManager/Settings"
        )

    cons = []
    conObjPaths = settings.ListConnections(dbus_interface="org.freedesktop.NetworkManager.Settings")
    for objPath in conObjPaths:
        con = bus.get_object("org.freedesktop.NetworkManager", objPath)
        settings = con.GetSettings(dbus_interface="org.freedesktop.NetworkManager.Settings.Connection")
        try:
            con_type = ConnectionType(str(settings["connection"]["type"]))
        except ValueError:
            con_type = ConnectionType.OTHER
        con_name = str(settings["connection"]["id"])
        con_uuid = str(settings["connection"]["uuid"])
        cons.append(NetworkManagerConnection(con_type, con_name, con_uuid))

    return cons

def get_all_active() -> list:
    bus = dbus.SystemBus()
    nm = bus.get_object(
        "org.freedesktop.NetworkManager",
        "/org/freedesktop/NetworkManager"
        )
    allConObjPaths = nm.GetAll(
        "org.freedesktop.NetworkManager",
        dbus_interface="org.freedesktop.DBus.Properties"
        )["ActiveConnections"]
    cons = []
    for conObjPath in allConObjPaths:
        con = bus.get_object("org.freedesktop.NetworkManager", conObjPath)
        iface = dbus.Interface(con, 'org.freedesktop.DBus.Properties')
        props = iface.GetAll("org.freedesktop.NetworkManager.Connection.Active")
        con_name = props["Id"]
        con_type = props["Type"]
        con_uuid = props["Uuid"]
        cons.append(NetworkManagerConnection(con_type, con_name, con_uuid))

    return cons
