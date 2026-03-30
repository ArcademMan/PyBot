"""Animated state indicator circle (idle / recording / playing)."""

from __future__ import annotations

import math

from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    Qt,
    Property,
)
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import QWidget

from pybot.ui.style import ACCENT, GREEN, RED


class StateIndicator(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._state = "idle"  # idle | recording | playing
        self._pulse = 0.0
        self._angle = 0.0

        # Pulse animation (recording)
        self._pulse_anim = QPropertyAnimation(self, b"pulse")
        self._pulse_anim.setDuration(1000)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setLoopCount(-1)

        # Rotation animation (playing)
        self._rotate_anim = QPropertyAnimation(self, b"angle")
        self._rotate_anim.setDuration(1200)
        self._rotate_anim.setStartValue(0.0)
        self._rotate_anim.setEndValue(360.0)
        self._rotate_anim.setLoopCount(-1)
        self._rotate_anim.setEasingCurve(QEasingCurve.Type.Linear)

    def set_state(self, state: str) -> None:
        self._pulse_anim.stop()
        self._rotate_anim.stop()
        self._state = state
        if state == "recording":
            self._pulse_anim.start()
        elif state == "playing":
            self._rotate_anim.start()
        self.update()

    # ── Qt properties for animation ───────────────
    def _get_pulse(self) -> float:
        return self._pulse

    def _set_pulse(self, v: float) -> None:
        self._pulse = v
        self.update()

    pulse = Property(float, _get_pulse, _set_pulse)

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, v: float) -> None:
        self._angle = v
        self.update()

    angle = Property(float, _get_angle, _set_angle)

    # ── Paint ─────────────────────────────────────
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        r = min(cx, cy) - 10

        color_map = {"idle": QColor(ACCENT), "recording": QColor(RED), "playing": QColor(GREEN)}
        base_color = color_map.get(self._state, QColor(ACCENT))

        # Background glow
        grad = QRadialGradient(cx, cy, r * 1.2)
        glow = QColor(base_color)
        glow.setAlpha(40)
        grad.setColorAt(0, glow)
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - r * 1.2), int(cy - r * 1.2), int(r * 2.4), int(r * 2.4))

        # Main circle
        p.setBrush(QColor(25, 25, 35, 200))
        pen = QPen(base_color, 3)
        p.setPen(pen)
        p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        if self._state == "recording":
            # Pulsing rings
            for i in range(3):
                phase = (self._pulse + i * 0.33) % 1.0
                ring_r = r * (0.6 + 0.5 * phase)
                alpha = int(120 * (1.0 - phase))
                ring_color = QColor(base_color)
                ring_color.setAlpha(alpha)
                p.setPen(QPen(ring_color, 2))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(int(cx - ring_r), int(cy - ring_r), int(ring_r * 2), int(ring_r * 2))

        elif self._state == "playing":
            # Rotating arc
            pen = QPen(base_color, 4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            arc_r = r * 0.75
            rect_x = int(cx - arc_r)
            rect_y = int(cy - arc_r)
            rect_sz = int(arc_r * 2)
            from PySide6.QtCore import QRectF
            p.drawArc(
                QRectF(rect_x, rect_y, rect_sz, rect_sz),
                int(self._angle * 16),
                90 * 16,
            )

        # Center icon text
        p.setPen(base_color)
        font = p.font()
        font.setPixelSize(28)
        font.setBold(True)
        p.setFont(font)
        label = {"idle": "\u23f8", "recording": "\u23fa", "playing": "\u25b6"}.get(self._state, "")
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, label)

        p.end()
