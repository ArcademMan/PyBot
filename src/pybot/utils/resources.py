"""Asset path resolution – works in dev mode and PyInstaller frozen mode."""

from __future__ import annotations

import sys
from pathlib import Path


def asset_path(relative: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS) / "assets"
    else:
        base = Path(__file__).resolve().parent.parent.parent.parent / "assets"
    return base / relative
