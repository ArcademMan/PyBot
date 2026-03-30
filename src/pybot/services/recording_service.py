"""Orchestrates the recorder and bridges to the Qt UI via signals."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from pybot.core.enums import RecordingState
from pybot.core.models import Macro, MacroMetadata
from pybot.core.recorder import Recorder


class RecordingService(QObject):
    state_changed = Signal(RecordingState)
    recording_finished = Signal(Macro)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._recorder: Recorder | None = None
        self._state = RecordingState.IDLE

    @property
    def state(self) -> RecordingState:
        return self._state

    @property
    def is_recording(self) -> bool:
        return self._state == RecordingState.RECORDING

    def toggle(
        self,
        record_movement: bool = True,
        record_clicks: bool = True,
        record_keyboard: bool = True,
        sample_ms: int = 20,
    ) -> None:
        if self.is_recording:
            self.stop()
        else:
            self.start(record_movement, record_clicks, record_keyboard, sample_ms)

    def start(
        self,
        record_movement: bool = True,
        record_clicks: bool = True,
        record_keyboard: bool = True,
        sample_ms: int = 20,
    ) -> None:
        if self.is_recording:
            return
        self._recorder = Recorder(
            record_mouse_movement=record_movement,
            record_mouse_clicks=record_clicks,
            record_keyboard=record_keyboard,
            sample_interval_ms=sample_ms,
        )
        self._recorder.start()
        self._state = RecordingState.RECORDING
        self.state_changed.emit(self._state)

    def stop(self) -> Macro | None:
        if not self.is_recording or not self._recorder:
            return None
        actions = self._recorder.stop()
        self._state = RecordingState.IDLE
        self.state_changed.emit(self._state)

        macro = Macro(metadata=MacroMetadata(), actions=actions)
        self.recording_finished.emit(macro)
        return macro
