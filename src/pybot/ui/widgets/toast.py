"""Slide-in toast notification widget."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QTimer,
    Qt,
    QPoint,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel, QWidget

from pybot.ui.style import ACCENT, GREEN, ORANGE, RED


_COLORS = {
    "info": ACCENT,
    "success": GREEN,
    "warning": ORANGE,
    "error": RED,
}


class Toast(QLabel):
    """A small notification that slides in from the top-right, stays, then fades out."""

    def __init__(self, parent: QWidget, message: str, variant: str = "info", duration_ms: int = 2500) -> None:
        super().__init__(parent)
        self._color = QColor(_COLORS.get(variant, ACCENT))
        self.setText(message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "background: transparent; border: none;"
            "color: #EAEAEA; font-size: 13px; font-weight: 600;"
            "padding: 10px 20px;"
        )
        self.adjustSize()
        self.setFixedSize(self.sizeHint().width() + 40, 42)

        # Start position (off-screen right, bottom)
        y = parent.height() - self.height() - 16
        start_x = parent.width() - self.width() - 16
        self._target = QPoint(start_x, y)
        self.move(parent.width() + 10, y)
        self.show()
        self.raise_()

        # Slide in
        self._anim_in = QPropertyAnimation(self, b"pos")
        self._anim_in.setDuration(300)
        self._anim_in.setStartValue(self.pos())
        self._anim_in.setEndValue(self._target)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Slide out
        self._anim_out = QPropertyAnimation(self, b"pos")
        self._anim_out.setDuration(300)
        self._anim_out.setStartValue(self._target)
        self._anim_out.setEndValue(QPoint(parent.width() + 10, y))
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.finished.connect(self.deleteLater)

        self._anim_in.start()
        QTimer.singleShot(duration_ms, self._anim_out.start)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = self.rect().adjusted(0, 0, -1, -1)
        path.addRoundedRect(rect, 10, 10)
        p.fillPath(path, QColor(30, 30, 45, 230))
        # Accent left strip
        strip = QPainterPath()
        strip.addRoundedRect(0, 0, 4, self.height(), 2, 2)
        p.fillPath(strip, self._color)
        # Border
        p.setPen(QColor(255, 255, 255, 15))
        p.drawPath(path)
        p.end()
        super().paintEvent(event)


def show_toast(parent: QWidget, message: str, variant: str = "info", duration_ms: int = 2500) -> Toast:
    """Convenience function to show a toast on any widget."""
    return Toast(parent, message, variant, duration_ms)
