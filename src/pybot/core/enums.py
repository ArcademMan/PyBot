"""Enumerations used across the application."""

from enum import Enum, auto


class ActionType(str, Enum):
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    MOUSE_CLICK = "mouse_click"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    DELAY = "delay"


class PlaybackState(Enum):
    IDLE = auto()
    PLAYING = auto()
    PAUSED = auto()


class RecordingState(Enum):
    IDLE = auto()
    RECORDING = auto()


class MouseButton(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
