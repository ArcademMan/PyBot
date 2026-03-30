"""Playback engine – replays macro actions via pynput controllers."""

from __future__ import annotations

import random
import time
from threading import Event

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

from pybot.core.models import Action, Macro, PlaybackConfig
from pybot.core.enums import ActionType

# Map pynput Key names for special keys
_SPECIAL_KEYS: dict[str, Key] = {k.name: k for k in Key}

_MOUSE_BUTTONS: dict[str, Button] = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}


class Player:
    def __init__(self) -> None:
        self._kb = keyboard.Controller()
        self._mouse = mouse.Controller()
        self._stop_event = Event()
        self._current_action_index = 0

    @property
    def current_index(self) -> int:
        return self._current_action_index

    def request_stop(self) -> None:
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def play(
        self,
        macro: Macro,
        config: PlaybackConfig | None = None,
        on_action: callable = None,
        on_loop: callable = None,
    ) -> None:
        """Play a macro. Blocks until complete or stopped.

        on_action(index): called before each action executes.
        on_loop(loop_number): called at the start of each loop.
        """
        cfg = config or macro.playback_config
        self._stop_event.clear()
        loops = cfg.loop_count if cfg.loop_count > 0 else float("inf")
        loop_num = 0

        while loop_num < loops:
            if self._stop_event.is_set():
                break

            if on_loop:
                on_loop(loop_num)

            for i, action in enumerate(macro.actions):
                if self._stop_event.is_set():
                    return
                self._current_action_index = i
                if on_action:
                    on_action(i)

                delay = action.delay_before / cfg.speed_multiplier
                if cfg.randomize_delays > 0:
                    jitter = delay * cfg.randomize_delays
                    delay += random.uniform(-jitter, jitter)
                    delay = max(0, delay)

                if delay > 0:
                    # Sleep in small chunks to allow fast stop
                    end = time.perf_counter() + delay
                    while time.perf_counter() < end:
                        if self._stop_event.is_set():
                            return
                        time.sleep(min(0.01, end - time.perf_counter()))

                self._execute(action)

            loop_num += 1
            if loop_num < loops and cfg.delay_between_loops > 0:
                end = time.perf_counter() + cfg.delay_between_loops
                while time.perf_counter() < end:
                    if self._stop_event.is_set():
                        return
                    time.sleep(min(0.01, end - time.perf_counter()))

    def _execute(self, action: Action) -> None:
        match action.type:
            case ActionType.KEY_PRESS:
                self._kb.press(self._resolve_key(action.key or ""))
            case ActionType.KEY_RELEASE:
                self._kb.release(self._resolve_key(action.key or ""))
            case ActionType.MOUSE_CLICK:
                self._mouse.position = (action.x or 0, action.y or 0)
                self._mouse.press(_MOUSE_BUTTONS.get(action.button or "left", Button.left))
            case ActionType.MOUSE_RELEASE:
                self._mouse.position = (action.x or 0, action.y or 0)
                self._mouse.release(_MOUSE_BUTTONS.get(action.button or "left", Button.left))
            case ActionType.MOUSE_MOVE:
                self._mouse.position = (action.x or 0, action.y or 0)
            case ActionType.MOUSE_SCROLL:
                self._mouse.position = (action.x or 0, action.y or 0)
                self._mouse.scroll(action.dx or 0, action.dy or 0)
            case ActionType.DELAY:
                pass  # delay already handled

    @staticmethod
    def _resolve_key(key_str: str) -> Key | KeyCode:
        if key_str in _SPECIAL_KEYS:
            return _SPECIAL_KEYS[key_str]
        if key_str.startswith("<") and key_str.endswith(">"):
            vk = int(key_str[1:-1])
            return KeyCode.from_vk(vk)
        if len(key_str) == 1:
            return KeyCode.from_char(key_str)
        return KeyCode.from_char(key_str)
