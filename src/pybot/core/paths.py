"""Centralized path management.

Convention:
  Windows: %APPDATA%/AmMstools/PyBot/
  Linux:   ~/.config/AmMstools/PyBot/
  Shared:  AmMstools/config.json → shared settings across all AmMstools apps
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "PyBot"

if sys.platform == "win32":
    _base = Path(os.environ.get("APPDATA", Path.home()))
else:
    _base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

ORG_ROOT = _base / "AmMstools"
APP_DIR = ORG_ROOT / APP_NAME
MACROS_DIR = APP_DIR / "macros"
SHARED_CONFIG = ORG_ROOT / "config.json"


def ensure_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    MACROS_DIR.mkdir(parents=True, exist_ok=True)


def load_shared_config() -> dict:
    if SHARED_CONFIG.exists():
        try:
            return json.loads(SHARED_CONFIG.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_shared_config(data: dict) -> None:
    ORG_ROOT.mkdir(parents=True, exist_ok=True)
    SHARED_CONFIG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_language() -> str:
    return load_shared_config().get("language", "en")
