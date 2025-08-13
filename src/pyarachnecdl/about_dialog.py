from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QHBoxLayout,
    )
from PyQt6.QtGui import (
    QIcon,
    )
from PyQt6.QtCore import (
    Qt
    )

from .version import VERSION

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        self.setWindowTitle(f"About {app.applicationDisplayName()}")

        icon = QToolButton()
        icon.setIcon(QIcon(app.icon_pixmap))
        icon.setMinimumHeight(48)
        icon.setMinimumWidth(48)

        msg = f"""
        {app.applicationDisplayName()}
        Version {VERSION}
        ⓒ 2025 Claas Nieslony
        """

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        button_box.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        for line in msg.split("\n")[1:]:
            if len(line) > 0:
                vbox.addWidget(QLabel(line.strip()))
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hbox.addWidget(icon)
        hbox.addLayout(vbox)

        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addWidget(button_box)
        self.setLayout(layout)
