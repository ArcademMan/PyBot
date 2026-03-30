"""QStackedWidget with crossfade page transitions."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QParallelAnimationGroup,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget


class AnimatedStack(QStackedWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._duration = 150

    def fade_to(self, index: int) -> None:
        if index == self.currentIndex() or index < 0 or index >= self.count():
            return

        old_widget = self.currentWidget()
        new_widget = self.widget(index)

        # Opacity effects
        old_effect = QGraphicsOpacityEffect(old_widget)
        old_widget.setGraphicsEffect(old_effect)
        new_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(new_effect)

        # Fade out old
        fade_out = QPropertyAnimation(old_effect, b"opacity")
        fade_out.setDuration(self._duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade in new
        fade_in = QPropertyAnimation(new_effect, b"opacity")
        fade_in.setDuration(self._duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade_out)
        group.addAnimation(fade_in)

        self.setCurrentIndex(index)

        def _cleanup():
            old_widget.setGraphicsEffect(None)
            new_widget.setGraphicsEffect(None)

        group.finished.connect(_cleanup)
        group.start()
