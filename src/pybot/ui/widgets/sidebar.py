"""Vertical sidebar navigation with icon buttons."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QWidget
import qtawesome as qta

from pybot.ui.style import ACCENT, ACCENT_DIM, TEXT, TEXT_SEC, SIDEBAR_BG


class SidebarButton(QPushButton):
    def __init__(self, icon_name: str, tooltip: str, parent=None) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self._active = False
        self.setFixedSize(48, 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self._update_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._update_style()

    def _update_style(self) -> None:
        color = ACCENT if self._active else TEXT
        self.setIcon(qta.icon(self._icon_name, color=color))
        self.setIconSize(QSize(22, 22))
        if self._active:
            self.setStyleSheet(
                f"QPushButton {{ background: {ACCENT_DIM}; border: none;"
                f"  border-left: 3px solid {ACCENT}; border-radius: 8px; }}"
                f"QPushButton:hover {{ background: {ACCENT_DIM}; }}"
            )
        else:
            self.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-radius: 8px; }"
                "QPushButton:hover { background: rgba(255,255,255,8); }"
            )


class Sidebar(QFrame):
    page_requested = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(62)
        self.setStyleSheet(f"Sidebar {{ background: {SIDEBAR_BG}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 12, 7, 16)
        layout.setSpacing(6)

        self._buttons: list[SidebarButton] = []
        self._entries: list[tuple[str, str]] = [
            ("mdi6.record-circle-outline", "Record"),
            ("mdi6.playlist-edit", "Editor"),
            ("mdi6.cog-outline", "Settings"),
        ]

        for i, (icon, tip) in enumerate(self._entries):
            btn = SidebarButton(icon, tip)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_click(idx))
            self._buttons.append(btn)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()

    def _on_click(self, index: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index)
        self.page_requested.emit(index)

    def set_active(self, index: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index)
