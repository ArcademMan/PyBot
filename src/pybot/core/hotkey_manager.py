"""Global hotkey registration and dispatch using pynput."""

from __future__ import annotations

from collections.abc import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(self) -> None:
        self._bindings: dict[str, Callable] = {}
        self._listener: keyboard.GlobalHotKeys | None = None

    def register(self, hotkey: str, callback: Callable) -> None:
        pynput_key = self._to_pynput_format(hotkey)
        self._bindings[pynput_key] = callback

    def start(self) -> None:
        if not self._bindings:
            return
        self.stop()
        self._listener = keyboard.GlobalHotKeys(self._bindings)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    def restart(self) -> None:
        self.stop()
        self.start()

    @staticmethod
    def _to_pynput_format(key: str) -> str:
        """Convert a simple key name like 'F9' or 'ctrl+shift+r' to pynput format."""
        parts = key.lower().split("+")
        result = []
        for p in parts:
            p = p.strip()
            match p:
                case "ctrl":
                    result.append("<ctrl>")
                case "alt":
                    result.append("<alt>")
                case "shift":
                    result.append("<shift>")
                case "cmd" | "win":
                    result.append("<cmd>")
                case s if s.startswith("f") and s[1:].isdigit():
                    result.append(f"<{s}>")
                case s if len(s) == 1:
                    result.append(s)
                case _:
                    result.append(f"<{p}>")
        return "+".join(result)
