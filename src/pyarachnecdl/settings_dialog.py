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
    QCheckBox
    )
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .settings import Settings, DownloadType, TimeUnit

class SettingsDialog(QDialog):
    def __init__(self, icon: QIcon):
        super().__init__()
        self.setWindowTitle("Download Settings")

        layout = QVBoxLayout()

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

        layout.addLayout(grid)
        layout.addStretch(1)

        buttons = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

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
