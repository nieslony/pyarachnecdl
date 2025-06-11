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
        self.allow_all_wifi = QCheckBox("Allow from all Wifi Connections")

        self.allow_all_wired = QCheckBox("Allow from all Wired Connections")

        self.allow_configured_vpn = QCheckBox("Allow from Configured VPN")

        self.available_connections = QListWidget()

        self.add_connection = QPushButton("Add")
        self.add_connection.setEnabled(False)
        self.add_all_connections = QPushButton("Add All")
        self.add_all_connections.setEnabled(False)
        self.remove_connection = QPushButton("Remove")
        self.remove_connection.setEnabled(False)
        self.remove_all_connections = QPushButton("Remove All")
        self.remove_all_connections.setEnabled(False)
        buttons = QVBoxLayout()
        buttons.addWidget(self.add_connection)
        buttons.addWidget(self.add_all_connections)
        buttons.addWidget(self.remove_connection)
        buttons.addWidget(self.remove_all_connections)
        buttons.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.allowed_connections = QListWidget()

        connections_grid = QGridLayout()
        connections_grid.addWidget(QLabel("Available Connections"), 0, 0)
        connections_grid.addWidget(self.available_connections, 1, 0)
        connections_grid.setColumnStretch(0, 1)

        connections_grid.addLayout(buttons, 1, 1)
        connections_grid.setColumnStretch(1, 0)

        connections_grid.addWidget(QLabel("Allowed Connections"), 0, 2)
        connections_grid.addWidget(self.allowed_connections, 1, 2)
        connections_grid.setColumnStretch(2, 1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.allow_all_wifi)
        vbox.addWidget(self.allow_all_wired)
        vbox.addWidget(self.allow_configured_vpn)
        vbox.addLayout(connections_grid, 1)
        widget = QWidget()
        widget.setLayout(vbox)

        self.available_connections.itemSelectionChanged.connect(
            self._on_available_connections_selection_changed
            )
        self.allowed_connections.itemSelectionChanged.connect(
            self._on_allowed_connections_selection_changed
            )
        self.add_connection.clicked.connect(self._on_add_connection_clicked)
        self.add_all_connections.clicked.connect(self._on_add_all_connections_clicked)
        self.remove_connection.clicked.connect(self._on_remove_connection_clicked)
        self.remove_all_connections.clicked.connect(self._on_remove_all_connections_clicked)

        return widget

    def _on_available_connections_selection_changed(self):
        enable = len(self.available_connections.selectedItems()) > 0
        self.add_connection.setEnabled(enable)
        self.add_all_connections.setEnabled(enable)

    def _on_allowed_connections_selection_changed(self):
        enable = len(self.allowed_connections.selectedItems()) > 0
        self.remove_connection.setEnabled(enable)
        self.remove_all_connections.setEnabled(enable)

    def _on_add_connection_clicked(self):
        items = self.available_connections.selectedItems()
        for i in items:
            self.available_connections.takeItem(self.available_connections.indexFromItem(i).row())
            self.allowed_connections.addItem(i)

    def _on_add_all_connections_clicked(self):
        for i in range(self.available_connections.count()-1, -1, -1):
            item = self.available_connections.takeItem(i)
            self.allowed_connections.insertItem(0, item)

    def _on_remove_connection_clicked(self):
        items = self.allowed_connections.selectedItems()
        for i in items:
            self.allowed_connections.takeItem(self.allowed_connections.indexFromItem(i).row())
            self.available_connections.addItem(i)

    def _on_remove_all_connections_clicked(self):
        for i in range(self.allowed_connections.count()-1, -1, -1):
            item = self.allowed_connections.takeItem(i)
            self.available_connections.insertItem(0, item)

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

        self.allow_all_wifi.setChecked(settings.allow_download_from_wifi)
        self.allow_all_wired.setChecked(settings.allow_download_from_wired)
        self.allow_configured_vpn.setChecked(settings.allow_download_from_vpn)

        allowed_connections = settings.allowed_connections
        for con in network_manager_connection.get_all():
            if con.con_type == network_manager_connection.ConnectionType.WIRED:
                item = QListWidgetItem(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWired), con.name)
            elif con.con_type == network_manager_connection.ConnectionType.WIFI:
                item = QListWidgetItem(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless), con.name)
            elif con.con_type == network_manager_connection.ConnectionType.VPN:
                item = QListWidgetItem(QIcon.fromTheme("network-vpn"), con.name)
            else:
                item = QListWidgetItem(con.name)
            item.setData(Qt.ItemDataRole.UserRole, con.uuid)
            if con.uuid in allowed_connections:
                self.allowed_connections.addItem(item)
            else:
                self.available_connections.addItem(item)

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

        settings.allow_download_from_wifi = self.allow_all_wifi.isChecked()
        settings.allow_download_from_wired = self.allow_all_wired.isChecked()
        settings.allow_download_from_vpn = self.allow_configured_vpn.isChecked()

        cons = []
        for i in range(self.allowed_connections.count()):
            item = self.allowed_connections.item(i)
            uuid = item.data(Qt.ItemDataRole.UserRole)
            cons.append(uuid)
        settings.allowed_connections = cons
