"""Filesystem-based macro storage in %APPDATA%/PyBot/macros/."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pybot.core.exceptions import MacroNotFoundError
from pybot.core.models import Macro, MacroMetadata
from pybot.utils.serialization import load_macro_json, save_macro_json


def _default_store_dir() -> Path:
    from pybot.core.paths import MACROS_DIR
    return MACROS_DIR


class MacroStore:
    def __init__(self, store_dir: Path | None = None) -> None:
        self._dir = store_dir or _default_store_dir()
        self._dir.mkdir(parents=True, exist_ok=True)

    @property
    def store_dir(self) -> Path:
        return self._dir

    def _path_for(self, macro_id: str) -> Path:
        return self._dir / f"{macro_id}.json"

    def save(self, macro: Macro) -> Path:
        macro.metadata.modified_at = datetime.now(timezone.utc).isoformat()
        path = self._path_for(macro.metadata.id)
        save_macro_json(macro, path)
        return path

    def load(self, macro_id: str) -> Macro:
        path = self._path_for(macro_id)
        if not path.exists():
            raise MacroNotFoundError(f"Macro {macro_id} not found")
        return load_macro_json(path)

    def delete(self, macro_id: str) -> None:
        path = self._path_for(macro_id)
        if path.exists():
            path.unlink()

    def list_macros(self) -> list[MacroMetadata]:
        result: list[MacroMetadata] = []
        for f in sorted(self._dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                macro = load_macro_json(f)
                result.append(macro.metadata)
            except Exception:
                continue
        return result

    def duplicate(self, macro_id: str, new_name: str | None = None) -> Macro:
        original = self.load(macro_id)
        import copy
        dup = copy.deepcopy(original)
        import uuid
        dup.metadata.id = str(uuid.uuid4())
        dup.metadata.name = new_name or f"{original.metadata.name} (copy)"
        dup.metadata.created_at = datetime.now(timezone.utc).isoformat()
        self.save(dup)
        return dup
