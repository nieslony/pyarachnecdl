import dbus

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QTabWidget,
    QWidget,
    QPushButton,
    QListWidget,
    QListWidgetItem
    )
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .settings import Settings, DownloadType, TimeUnit
from . import network_manager_connection

class SettingsDialog(QDialog):
    def __init__(self, icon: QIcon):
        super().__init__()
        self.setWindowTitle("Download Settings")
        self.setWindowIcon(icon)

        tabs = QTabWidget()
        tabs.addTab(self._create_basics_tab(), "Basics")
        tabs.addTab(self._create_allowed_networks_tab(), "Allowed Networks")

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def _create_allowed_networks_tab(self) -> QWidget:
        self.allowAllWifi = QCheckBox("Allow from all Wifi Connections")

        self.allowAllWired = QCheckBox("Allow from all Wired Connections")

        self.allowConfiguredVpn = QCheckBox("Allow from Configured VPN")

        self.availableConnections = QListWidget()

        self.addConnection = QPushButton("Add")
        self.addConnection.setEnabled(False)
        self.addAllConnections = QPushButton("Add All")
        self.addAllConnections.setEnabled(False)
        self.removeConnection = QPushButton("Remove")
        self.removeConnection.setEnabled(False)
        self.removeAllConnections = QPushButton("Remove All")
        self.removeAllConnections.setEnabled(False)
        buttons = QVBoxLayout()
        buttons.addWidget(self.addConnection)
        buttons.addWidget(self.addAllConnections)
        buttons.addWidget(self.removeConnection)
        buttons.addWidget(self.removeAllConnections)
        buttons.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.allowedConnections = QListWidget()

        connectionsGrid = QGridLayout()
        connectionsGrid.addWidget(QLabel("Available Connections"), 0, 0)
        connectionsGrid.addWidget(self.availableConnections, 1, 0)
        connectionsGrid.setColumnStretch(0, 1)

        connectionsGrid.addLayout(buttons, 1, 1)
        connectionsGrid.setColumnStretch(1, 0)

        connectionsGrid.addWidget(QLabel("Allowed Connections"), 0, 2)
        connectionsGrid.addWidget(self.allowedConnections, 1, 2)
        connectionsGrid.setColumnStretch(2, 1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.allowAllWifi)
        vbox.addWidget(self.allowAllWired)
        vbox.addWidget(self.allowConfiguredVpn)
        vbox.addLayout(connectionsGrid, 1)
        widget = QWidget()
        widget.setLayout(vbox)

        self.availableConnections.itemSelectionChanged.connect(self._on_availableConnections_selection_changed)
        self.allowedConnections.itemSelectionChanged.connect(self._on_allowedConnections_selection_changed)
        self.addConnection.clicked.connect(self._on_addConnection_clicked)
        self.addAllConnections.clicked.connect(self._on_addAllConnections_clicked)
        self.removeConnection.clicked.connect(self._on_removeConnection_clicked)
        self.removeAllConnections.clicked.connect(self._on_removeAllConnections_clicked)

        return widget

    def _on_availableConnections_selection_changed(self):
        enable = len(self.availableConnections.selectedItems()) > 0
        self.addConnection.setEnabled(enable);
        self.addAllConnections.setEnabled(enable)

    def _on_allowedConnections_selection_changed(self):
        enable = len(self.allowedConnections.selectedItems()) > 0
        self.removeConnection.setEnabled(enable);
        self.removeAllConnections.setEnabled(enable)

    def _on_addConnection_clicked(self):
        items = self.availableConnections.selectedItems()
        for i in items:
            self.availableConnections.takeItem(self.availableConnections.indexFromItem(i).row())
            self.allowedConnections.addItem(i)

    def _on_addAllConnections_clicked(self):
        for i in range(self.availableConnections.count()-1, -1, -1):
            item = self.availableConnections.takeItem(i)
            self.allowedConnections.insertItem(0, item)

    def _on_removeConnection_clicked(self):
        items = self.allowedConnections.selectedItems()
        for i in items:
            self.allowedConnections.takeItem(self.allowedConnections.indexFromItem(i).row())
            self.availableConnections.addItem(i)

    def _on_removeAllConnections_clicked(self):
        for i in range(self.allowedConnections.count()-1, -1, -1):
            item = self.allowedConnections.takeItem(i)
            self.availableConnections.insertItem(0, item)

    def _create_basics_tab(self) -> QWidget:
        grid = QGridLayout()
        cur_line = 0

        grid.addWidget(QLabel("Admin Server URL:"), cur_line, 0)
        self.admin_server_url = QLineEdit()
        self.admin_server_url.setMinimumWidth(self.fontMetrics().averageCharWidth() * 50)
        hbox = QHBoxLayout()
        hbox.addWidget(self.admin_server_url, 1)
        hbox.addWidget(QLabel("/api/openvpn/user_config"), cur_line)
        grid.addLayout(hbox, cur_line, 1)
        cur_line += 1

        self.ignore_ssl_error = QCheckBox("Ignore SSL errors")
        grid.addWidget(self.ignore_ssl_error, cur_line, 1)
        cur_line += 1

        self.download_periodically = QCheckBox("Download periodically")
        self.download_periodically.checkStateChanged.connect(self._on_change_download_periodically)
        grid.addWidget(self.download_periodically, cur_line, 1)
        cur_line += 1

        grid.addWidget(QLabel("Download Delay:"), cur_line, 0)
        self.download_delay = QSpinBox()
        self.download_delay.setMinimum(1)
        self.download_delay.setEnabled(False)

        self.download_delay_unit = QComboBox()
        for tu in TimeUnit:
            self.download_delay_unit.addItem(tu.value, tu)
        self.download_delay_unit.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(self.download_delay)
        hbox.addWidget(self.download_delay_unit)
        grid.addLayout(hbox, cur_line, 1)
        cur_line += 1

        grid.addWidget(QLabel("Download Interval:"), cur_line, 0)
        self.download_interval = QSpinBox()
        self.download_interval.setMinimum(1)
        self.download_interval.setEnabled(False)

        self.download_interval_unit = QComboBox()
        for tu in TimeUnit:
            self.download_interval_unit.addItem(tu.value, tu)
        self.download_interval_unit.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(self.download_interval)
        hbox.addWidget(self.download_interval_unit)
        grid.addLayout(hbox, cur_line, 1)
        cur_line += 1

        grid.addWidget(QLabel("Download Type:"))
        self.download_type = QComboBox()
        for dt in DownloadType:
            self.download_type.addItem(dt.value, dt)
        self.download_type.currentIndexChanged.connect(self._on_change_download_type)
        grid.addWidget(self.download_type, cur_line, 1)
        cur_line += 1

        grid.addWidget(QLabel("Download Destination:"))
        self.download_destination = QLineEdit()
        self.download_destination.setEnabled(False)
        grid.addWidget(self.download_destination, cur_line, 1)
        cur_line += 1

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addStretch(1)
        widget.setLayout(layout)

        return widget

    def _on_change_download_periodically(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self.download_delay.setEnabled(True)
            self.download_delay_unit.setEnabled(True)
            self.download_interval.setEnabled(True)
            self.download_interval_unit.setEnabled(True)
        elif state == Qt.CheckState.Unchecked:
            self.download_delay.setEnabled(False)
            self.download_delay_unit.setEnabled(False)
            self.download_interval.setEnabled(False)
            self.download_interval_unit.setEnabled(False)

    def _on_change_download_type(self, index: int):
        self.download_destination.setEnabled(list(DownloadType)[index] == DownloadType.OVPN)

    def load_settings(self, settings: Settings):
        self.admin_server_url.setText(settings.admin_server_url)
        self.ignore_ssl_error.setChecked(settings.ignore_ssl_errors)
        self.download_periodically.setChecked(settings.auto_download)
        self.download_interval.setValue(settings.download_interval)
        self.download_interval_unit.setCurrentIndex(
            self.download_interval_unit.findData(settings.download_interval_unit)
            )
        self.download_delay.setValue(settings.download_delay)
        self.download_delay_unit.setCurrentIndex(
            self.download_delay_unit.findData(settings.download_delay_unit)
            )
        self.download_type.setCurrentIndex(
            self.download_type.findData(settings.download_type)
            )
        self.download_destination.setText(settings.download_destination)

        self.allowAllWifi.setChecked(settings.allow_download_from_wifi)
        self.allowAllWired.setChecked(settings.allow_download_from_wired)
        self.allowConfiguredVpn.setChecked(settings.allow_download_from_vpn)

        allowedConnections = settings.allowed_connections
        for con in network_manager_connection.get_all():
            if con.con_type == network_manager_connection.ConnectionType.WIRED:
                item = QListWidgetItem(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWired), con.name)
            elif con.con_type == network_manager_connection.ConnectionType.WIFI:
                item = QListWidgetItem(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless), con.name)
            elif con.con_type == network_manager_connection.ConnectionType.VPN:
                item = QListWidgetItem(QIcon.fromTheme(u"network-vpn"), con.name)
            else:
                item = QListWidgetItem(con.name)
            item.setData(Qt.ItemDataRole.UserRole, con.uuid)
            if con.uuid in allowedConnections:
                self.allowedConnections.addItem(item)
            else:
                self.availableConnections.addItem(item)

    def save_settings(self, settings: Settings):
        settings.admin_server_url = self.admin_server_url.text()
        settings.ignore_ssl_error = self.ignore_ssl_error.isChecked()
        settings.auto_download = self.download_periodically.isChecked()
        settings.download_interval = self.download_interval.value()
        settings.download_interval_unit = self.download_interval_unit.currentData()
        settings.download_delay = self.download_delay.value()
        settings.download_delay_unit = self.download_delay_unit.currentData()
        settings.download_type = self.download_type.currentData()
        settings.download_destination = self.download_destination.text()

        settings.allow_download_from_wifi = self.allowAllWifi.isChecked()
        settings.allow_download_from_wired = self.allowAllWired.isChecked()
        settings.allow_download_from_vpn = self.allowConfiguredVpn.isChecked()

        cons = []
        for i in range(self.allowedConnections.count()):
            item = self.allowedConnections.item(i)
            uuid = item.data(Qt.ItemDataRole.UserRole)
            cons.append(uuid)
        settings.allowed_connections = cons
