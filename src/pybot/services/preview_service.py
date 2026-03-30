"""Preview service – dry-run playback that moves the mouse and shows action labels."""

from __future__ import annotations

import time
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal

from pybot.core.enums import ActionType, PlaybackState
from pybot.core.models import Action, Macro, PlaybackConfig


class _PreviewWorker(QObject):
    """Runs on a QThread. Emits signals instead of executing real actions."""

    # (x, y, list_of_(label, action_type))
    show_actions = Signal(int, int, list)
    move_mouse = Signal(int, int)
    clear_overlay = Signal()
    finished = Signal()

    def __init__(self, macro: Macro, config: PlaybackConfig) -> None:
        super().__init__()
        self._macro = macro
        self._config = config
        self._stop = Event()

    def request_stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        try:
            self._run_impl()
        except Exception:
            pass
        finally:
            self.clear_overlay.emit()
            self.finished.emit()

    def _run_impl(self) -> None:
        actions = self._macro.actions
        cfg = self._config
        self._stop.clear()

        for i, action in enumerate(actions):
            if self._stop.is_set():
                return

            # Respect timing
            delay = action.delay_before / cfg.speed_multiplier
            if delay > 0:
                end = time.perf_counter() + delay
                while time.perf_counter() < end:
                    if self._stop.is_set():
                        return
                    time.sleep(max(0, min(0.01, end - time.perf_counter())))

            if self._stop.is_set():
                return

            # Get cursor target position from this action or keep last known
            x, y = self._action_pos(action)

            # Move the real mouse for movement actions only
            if action.type == ActionType.MOUSE_MOVE:
                self.move_mouse.emit(x, y)

            # Skip pure move/delay from label display
            if action.type in (ActionType.MOUSE_MOVE, ActionType.DELAY):
                self.clear_overlay.emit()
                continue

            # Gather simultaneous actions (same timestamp)
            # Each entry is [label_str, action_type_value_str]
            batch: list[list[str]] = []
            batch.append([action.human_detail(), action.type.value])

            # Look ahead for actions at the same timestamp
            j = i + 1
            while j < len(actions) and abs(actions[j].timestamp - action.timestamp) < 0.005:
                a = actions[j]
                if a.type not in (ActionType.MOUSE_MOVE, ActionType.DELAY):
                    batch.append([a.human_detail(), a.type.value])
                j += 1

            self.show_actions.emit(x, y, batch)

        # Brief pause to see the last label
        end = time.perf_counter() + 0.5
        while time.perf_counter() < end:
            if self._stop.is_set():
                return
            time.sleep(0.01)

    @staticmethod
    def _action_pos(action: Action) -> tuple[int, int]:
        """Extract screen coordinates from an action, defaulting to (0, 0)."""
        return (action.x or 0, action.y or 0)


class PreviewService(QObject):
    state_changed = Signal(PlaybackState)
    # Forwarded from worker for overlay control
    show_actions = Signal(int, int, list)
    move_mouse = Signal(int, int)
    clear_overlay = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _PreviewWorker | None = None
        self._state = PlaybackState.IDLE

    @property
    def is_previewing(self) -> bool:
        return self._state == PlaybackState.PLAYING

    def preview(self, macro: Macro, config: PlaybackConfig | None = None) -> None:
        if self.is_previewing:
            return
        cfg = config or macro.playback_config

        self._thread = QThread()
        self._worker = _PreviewWorker(macro, cfg)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.show_actions.connect(self.show_actions.emit)
        self._worker.move_mouse.connect(self.move_mouse.emit)
        self._worker.clear_overlay.connect(self.clear_overlay.emit)
        self._worker.finished.connect(self._on_finished)

        self._state = PlaybackState.PLAYING
        self.state_changed.emit(self._state)
        self._thread.start()

    def stop(self) -> None:
        if not self.is_previewing:
            return
        if self._worker:
            self._worker.request_stop()

    def _on_finished(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
        self._worker = None
        self._state = PlaybackState.IDLE
        self.state_changed.emit(self._state)
