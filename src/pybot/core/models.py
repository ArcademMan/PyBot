"""Data models for macros and actions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pybot.core.enums import ActionType


@dataclass
class Action:
    type: ActionType
    timestamp: float  # seconds since macro start (immutable reference)
    delay_before: float  # seconds to wait before executing
    key: str | None = None
    x: int | None = None
    y: int | None = None
    button: str | None = None
    dx: int | None = None
    dy: int | None = None

    def human_detail(self) -> str:
        match self.type:
            case ActionType.KEY_PRESS | ActionType.KEY_RELEASE:
                arrow = "\u2193" if self.type == ActionType.KEY_PRESS else "\u2191"
                return f"{arrow} {self.key}"
            case ActionType.MOUSE_CLICK | ActionType.MOUSE_RELEASE:
                arrow = "\u2193" if self.type == ActionType.MOUSE_CLICK else "\u2191"
                return f"{arrow} {self.button} ({self.x}, {self.y})"
            case ActionType.MOUSE_MOVE:
                return f"({self.x}, {self.y})"
            case ActionType.MOUSE_SCROLL:
                return f"({self.x}, {self.y}) d={self.dy}"
            case ActionType.DELAY:
                return f"{self.delay_before:.3f}s"
            case _:
                return ""

    def human_type(self) -> str:
        return {
            ActionType.KEY_PRESS: "Key \u2193",
            ActionType.KEY_RELEASE: "Key \u2191",
            ActionType.MOUSE_CLICK: "Click",
            ActionType.MOUSE_RELEASE: "Release",
            ActionType.MOUSE_MOVE: "Move",
            ActionType.MOUSE_SCROLL: "Scroll",
            ActionType.DELAY: "Delay",
        }.get(self.type, self.type.value)


@dataclass
class PlaybackConfig:
    speed_multiplier: float = 1.0
    loop_count: int = 1  # 0 = infinite
    delay_between_loops: float = 0.0
    randomize_delays: float = 0.0  # 0.0-1.0 jitter factor


@dataclass
class MacroMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Macro"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    modified_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    description: str = ""
    category: str = ""
    hotkey: str = ""  # per-macro launch hotkey, e.g. "ctrl+F1"


@dataclass
class Macro:
    metadata: MacroMetadata = field(default_factory=MacroMetadata)
    playback_config: PlaybackConfig = field(default_factory=PlaybackConfig)
    actions: list[Action] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.metadata.name

    @name.setter
    def name(self, value: str) -> None:
        self.metadata.name = value

    @property
    def action_count(self) -> int:
        return len(self.actions)

    @property
    def duration(self) -> float:
        if not self.actions:
            return 0.0
        return self.actions[-1].timestamp
