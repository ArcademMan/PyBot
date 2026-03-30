"""Orchestrates the player on a QThread, bridges signals to UI."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from pybot.core.enums import PlaybackState
from pybot.core.models import Macro, PlaybackConfig
from pybot.core.player import Player


class _PlayWorker(QObject):
    action_executing = Signal(int)
    loop_started = Signal(int)
    finished = Signal()

    def __init__(self, player: Player, macro: Macro, config: PlaybackConfig) -> None:
        super().__init__()
        self._player = player
        self._macro = macro
        self._config = config

    def run(self) -> None:
        self._player.play(
            self._macro,
            self._config,
            on_action=lambda i: self.action_executing.emit(i),
            on_loop=lambda n: self.loop_started.emit(n),
        )
        self.finished.emit()


class PlaybackService(QObject):
    state_changed = Signal(PlaybackState)
    action_executing = Signal(int)
    loop_started = Signal(int)
    playback_finished = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._player = Player()
        self._thread: QThread | None = None
        self._worker: _PlayWorker | None = None
        self._state = PlaybackState.IDLE

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def is_playing(self) -> bool:
        return self._state == PlaybackState.PLAYING

    def play(self, macro: Macro, config: PlaybackConfig | None = None) -> None:
        if self.is_playing:
            return
        cfg = config or macro.playback_config

        self._player = Player()
        self._thread = QThread()
        self._worker = _PlayWorker(self._player, macro, cfg)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.action_executing.connect(self.action_executing.emit)
        self._worker.loop_started.connect(self.loop_started.emit)
        self._worker.finished.connect(self._on_finished)

        self._state = PlaybackState.PLAYING
        self.state_changed.emit(self._state)
        self._thread.start()

    def stop(self) -> None:
        if not self.is_playing:
            return
        self._player.request_stop()

    def _on_finished(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
        self._worker = None
        self._state = PlaybackState.IDLE
        self.state_changed.emit(self._state)
        self.playback_finished.emit()
