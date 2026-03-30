"""Floating overlay that shows action labels near the cursor during preview."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget

from pybot.core.enums import ActionType

# Label colours by action category
_COLORS: dict[str, QColor] = {
    "key": QColor(124, 92, 252, 230),     # accent purple
    "click": QColor(76, 175, 80, 230),    # green
    "scroll": QColor(255, 152, 0, 230),   # orange
    "move": QColor(100, 100, 120, 180),   # grey
    "delay": QColor(136, 136, 136, 180),  # dim grey
}


def _color_for(action_type: ActionType) -> QColor:
    if action_type in (ActionType.KEY_PRESS, ActionType.KEY_RELEASE):
        return _COLORS["key"]
    if action_type in (ActionType.MOUSE_CLICK, ActionType.MOUSE_RELEASE):
        return _COLORS["click"]
    if action_type == ActionType.MOUSE_SCROLL:
        return _COLORS["scroll"]
    if action_type == ActionType.MOUSE_MOVE:
        return _COLORS["move"]
    return _COLORS["delay"]


class PreviewOverlay(QWidget):
    """Transparent, click-through overlay that renders action badges near the cursor."""

    BADGE_H = 28
    BADGE_PAD = 8
    BADGE_GAP = 4
    CURSOR_OFFSET = QPoint(18, -10)  # offset from cursor position

    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._labels: list[tuple[str, QColor]] = []
        self._font = QFont("Segoe UI", 10, QFont.Weight.DemiBold)

    # ── Public API ──────────────────────────────
    def show_actions(self, x: int, y: int, labels: list) -> None:
        """Display action badges at screen position (x, y).

        labels: list of [text, action_type_value] pairs (strings).
        """
        self._labels = [
            (entry[0], _color_for(ActionType(entry[1]))) for entry in labels
        ]
        self._reposition(x, y)
        self.update()
        if not self.isVisible():
            self.show()

    def clear(self) -> None:
        self._labels.clear()
        self.hide()

    # ── Positioning ─────────────────────────────
    def _reposition(self, cx: int, cy: int) -> None:
        fm = self.fontMetrics()
        if not self._labels:
            return
        max_w = max(fm.horizontalAdvance(t) for t, _ in self._labels) + self.BADGE_PAD * 2 + 4
        total_h = len(self._labels) * (self.BADGE_H + self.BADGE_GAP)
        w = max_w + 4
        h = total_h + 4
        # Position above-right of cursor
        pos = QPoint(cx, cy) + self.CURSOR_OFFSET - QPoint(0, h)
        self.setGeometry(pos.x(), pos.y(), w, h)

    # ── Paint ───────────────────────────────────
    def paintEvent(self, event) -> None:
        if not self._labels:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(self._font)

        y = 2
        for text, color in self._labels:
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(text)
            bw = tw + self.BADGE_PAD * 2
            # Background
            path = QPainterPath()
            path.addRoundedRect(2, y, bw, self.BADGE_H, 6, 6)
            p.fillPath(path, color)
            # Border
            p.setPen(QColor(255, 255, 255, 60))
            p.drawPath(path)
            # Text
            p.setPen(QColor(255, 255, 255, 240))
            p.drawText(2 + self.BADGE_PAD, y + self.BADGE_H - 8, text)
            y += self.BADGE_H + self.BADGE_GAP

        p.end()
