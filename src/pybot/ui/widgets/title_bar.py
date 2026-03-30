"""Custom frameless title bar with drag support."""

from __future__ import annotations

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
import qtawesome as qta

from pybot.ui.style import TEXT_SEC


class TitleBar(QFrame):
    def __init__(self, window, parent=None) -> None:
        super().__init__(parent)
        self._window = window
        self._drag_pos: QPoint | None = None
        self.setFixedHeight(38)
        self.setStyleSheet(
            "TitleBar {"
            "  background: rgba(15, 15, 25, 240);"
            "  border-top-left-radius: 12px;"
            "  border-top-right-radius: 12px;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)

        title = QLabel("PyBot")
        title.setStyleSheet("font-weight: 700; font-size: 13px; color: #EAEAEA;")
        layout.addWidget(title)
        layout.addStretch()

        for icon, slot, hover in [
            ("mdi6.minus", self._window.showMinimized, "rgba(255,255,255,10)"),
            ("mdi6.close", self._window.close, "rgba(244,67,54,180)"),
        ]:
            btn = QPushButton()
            btn.setIcon(qta.icon(icon, color=TEXT_SEC))
            btn.setFixedSize(32, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: none; border-radius: 6px; }}"
                f"QPushButton:hover {{ background: {hover}; }}"
            )
            btn.clicked.connect(slot)
            layout.addWidget(btn)

    # ── Drag support ──────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
