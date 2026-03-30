"""Custom exception hierarchy."""


class PyBotError(Exception):
    pass


class MacroNotFoundError(PyBotError):
    pass


class RecordingError(PyBotError):
    pass


class PlaybackError(PyBotError):
    pass
