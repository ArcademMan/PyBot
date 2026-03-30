"""Semi-transparent card with glassmorphism effect."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QFrame, QVBoxLayout


class GlassCard(QFrame):
    """Card drawn via paintEvent so child widgets are NOT affected by stylesheet."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)

    def body(self) -> QVBoxLayout:
        return self._layout

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        p.fillPath(path, QColor(255, 255, 255, 8))
        p.setPen(QColor(255, 255, 255, 12))
        p.drawPath(path)
        p.end()
