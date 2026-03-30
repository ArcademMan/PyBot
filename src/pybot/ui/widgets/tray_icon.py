"""System tray icon with context menu."""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon
import qtawesome as qta


class TrayIcon(QSystemTrayIcon):
    def __init__(self, window, parent=None) -> None:
        super().__init__(parent)
        self._window = window
        self.setIcon(qta.icon("mdi6.robot-outline", color="#7C5CFC"))
        self.setToolTip("PyBot")

        menu = QMenu()
        show_action = menu.addAction("Show / Hide")
        show_action.triggered.connect(self._toggle_window)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit)
        self.setContextMenu(menu)

        self.activated.connect(self._on_activated)

    def _toggle_window(self) -> None:
        if self._window.isVisible():
            self._window.hide()
        else:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_window()

    def _quit(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
