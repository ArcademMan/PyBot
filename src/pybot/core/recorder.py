"""Recording engine – captures keyboard and mouse events via pynput."""

from __future__ import annotations

import time
from threading import Lock

from pynput import keyboard, mouse

from pybot.core.enums import ActionType
from pybot.core.models import Action


class Recorder:
    def __init__(
        self,
        record_mouse_movement: bool = True,
        record_mouse_clicks: bool = True,
        record_keyboard: bool = True,
        sample_interval_ms: int = 20,
    ) -> None:
        self._record_mouse_movement = record_mouse_movement
        self._record_mouse_clicks = record_mouse_clicks
        self._record_keyboard = record_keyboard
        self._sample_interval = sample_interval_ms / 1000.0
        self._actions: list[Action] = []
        self._lock = Lock()
        self._start_time: float = 0.0
        self._last_move_time: float = 0.0
        self._kb_listener: keyboard.Listener | None = None
        self._mouse_listener: mouse.Listener | None = None
        self._running = False

    @property
    def actions(self) -> list[Action]:
        with self._lock:
            return list(self._actions)

    def start(self) -> None:
        self._actions.clear()
        self._start_time = time.perf_counter()
        self._last_move_time = 0.0
        self._running = True

        if self._record_keyboard:
            self._kb_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
            )
            self._kb_listener.start()

        needs_mouse = self._record_mouse_clicks or self._record_mouse_movement
        if needs_mouse:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_click if self._record_mouse_clicks else None,
                on_scroll=self._on_scroll if self._record_mouse_clicks else None,
                on_move=self._on_move if self._record_mouse_movement else None,
            )
            self._mouse_listener.start()

    def stop(self) -> list[Action]:
        self._running = False
        if self._kb_listener:
            self._kb_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()
        return self._finalize()

    def _elapsed(self) -> float:
        return time.perf_counter() - self._start_time

    def _append(self, action: Action) -> None:
        with self._lock:
            self._actions.append(action)

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if not self._running:
            return
        t = self._elapsed()
        self._append(Action(
            type=ActionType.KEY_PRESS,
            timestamp=t,
            delay_before=0,
            key=self._key_to_str(key),
        ))

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if not self._running:
            return
        t = self._elapsed()
        self._append(Action(
            type=ActionType.KEY_RELEASE,
            timestamp=t,
            delay_before=0,
            key=self._key_to_str(key),
        ))

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if not self._running:
            return
        t = self._elapsed()
        self._append(Action(
            type=ActionType.MOUSE_CLICK if pressed else ActionType.MOUSE_RELEASE,
            timestamp=t,
            delay_before=0,
            x=int(x),
            y=int(y),
            button=button.name,
        ))

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self._running:
            return
        t = self._elapsed()
        self._append(Action(
            type=ActionType.MOUSE_SCROLL,
            timestamp=t,
            delay_before=0,
            x=int(x),
            y=int(y),
            dx=int(dx),
            dy=int(dy),
        ))

    def _on_move(self, x: int, y: int) -> None:
        if not self._running:
            return
        t = self._elapsed()
        if t - self._last_move_time < self._sample_interval:
            return
        self._last_move_time = t
        self._append(Action(
            type=ActionType.MOUSE_MOVE,
            timestamp=t,
            delay_before=0,
            x=int(x),
            y=int(y),
        ))

    def _finalize(self) -> list[Action]:
        """Compute delay_before for each action based on timestamps."""
        with self._lock:
            for i, action in enumerate(self._actions):
                if i == 0:
                    action.delay_before = action.timestamp
                else:
                    action.delay_before = action.timestamp - self._actions[i - 1].timestamp
            return list(self._actions)

    @staticmethod
    def _key_to_str(key: keyboard.Key | keyboard.KeyCode | None) -> str:
        if key is None:
            return "unknown"
        if isinstance(key, keyboard.Key):
            return key.name
        if isinstance(key, keyboard.KeyCode):
            if key.char:
                return key.char
            if key.vk:
                return f"<{key.vk}>"
        return str(key)
