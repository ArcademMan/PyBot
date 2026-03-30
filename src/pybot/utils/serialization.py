"""JSON serialization for Macro dataclasses."""

from __future__ import annotations

import json
from pathlib import Path

from pybot.core.enums import ActionType
from pybot.core.models import Action, Macro, MacroMetadata, PlaybackConfig

SCHEMA_VERSION = 1


def macro_to_dict(macro: Macro) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "id": macro.metadata.id,
            "name": macro.metadata.name,
            "created_at": macro.metadata.created_at,
            "modified_at": macro.metadata.modified_at,
            "description": macro.metadata.description,
            "category": macro.metadata.category,
            "hotkey": macro.metadata.hotkey,
        },
        "playback_config": {
            "speed_multiplier": macro.playback_config.speed_multiplier,
            "loop_count": macro.playback_config.loop_count,
            "delay_between_loops": macro.playback_config.delay_between_loops,
            "randomize_delays": macro.playback_config.randomize_delays,
        },
        "actions": [_action_to_dict(a) for a in macro.actions],
    }


def macro_from_dict(data: dict) -> Macro:
    md = data["metadata"]
    pc = data.get("playback_config", {})
    return Macro(
        metadata=MacroMetadata(
            id=md["id"],
            name=md["name"],
            created_at=md.get("created_at", ""),
            modified_at=md.get("modified_at", ""),
            description=md.get("description", ""),
            category=md.get("category", ""),
            hotkey=md.get("hotkey", ""),
        ),
        playback_config=PlaybackConfig(
            speed_multiplier=pc.get("speed_multiplier", 1.0),
            loop_count=pc.get("loop_count", 1),
            delay_between_loops=pc.get("delay_between_loops", 0.0),
            randomize_delays=pc.get("randomize_delays", 0.0),
        ),
        actions=[_action_from_dict(a) for a in data.get("actions", [])],
    )


def save_macro_json(macro: Macro, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(macro_to_dict(macro), indent=2, ensure_ascii=False), encoding="utf-8")


def load_macro_json(path: Path) -> Macro:
    data = json.loads(path.read_text(encoding="utf-8"))
    return macro_from_dict(data)


def _action_to_dict(a: Action) -> dict:
    d: dict = {
        "type": a.type.value,
        "timestamp": a.timestamp,
        "delay_before": a.delay_before,
    }
    for attr in ("key", "x", "y", "button", "dx", "dy"):
        v = getattr(a, attr)
        if v is not None:
            d[attr] = v
    return d


def _action_from_dict(d: dict) -> Action:
    return Action(
        type=ActionType(d["type"]),
        timestamp=d["timestamp"],
        delay_before=d["delay_before"],
        key=d.get("key"),
        x=d.get("x"),
        y=d.get("y"),
        button=d.get("button"),
        dx=d.get("dx"),
        dy=d.get("dy"),
    )
