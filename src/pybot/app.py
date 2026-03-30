"""Application entry point – QApplication setup and launch."""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pybot.ui.style import STYLESHEET
from pybot.ui.main_window import MainWindow
from pybot.utils.resources import asset_path


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PyBot")
    app.setOrganizationName("PyBot")
    app.setStyleSheet(STYLESHEET)

    icon = QIcon(str(asset_path("icon.png")))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
