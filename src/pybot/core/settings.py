"""Application settings – stored as JSON in AmMstools/PyBot/settings.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AppSettings:
    # Hotkeys
    hotkey_record: str = "F9"
    hotkey_play: str = "F6"
    hotkey_stop: str = "F12"

    # Recording
    record_mouse_movement: bool = True
    mouse_sample_interval_ms: int = 20

    # Playback
    default_speed: float = 1.0
    default_loops: int = 1
    default_delay_between_loops: float = 0.0

    # UI
    minimize_to_tray: bool = True
    start_minimized: bool = False

    @staticmethod
    def _path() -> Path:
        from pybot.core.paths import APP_DIR
        return APP_DIR / "settings.json"

    def save(self) -> None:
        p = self._path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls) -> AppSettings:
        p = cls._path()
        if not p.exists():
            return cls()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            settings = cls()
            for k, v in data.items():
                if hasattr(settings, k):
                    expected = type(getattr(settings, k))
                    setattr(settings, k, expected(v))
            return settings
        except Exception:
            return cls()
