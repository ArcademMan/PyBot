"""CRUD operations for macros + undo/redo stack."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from pybot.core.macro_store import MacroStore
from pybot.core.models import Macro, MacroMetadata


class MacroService(QObject):
    macro_saved = Signal(str)       # macro_id
    macro_deleted = Signal(str)     # macro_id
    macro_list_changed = Signal()

    def __init__(self, store: MacroStore | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._store = store or MacroStore()

    @property
    def store(self) -> MacroStore:
        return self._store

    def list_macros(self) -> list[MacroMetadata]:
        return self._store.list_macros()

    def load(self, macro_id: str) -> Macro:
        return self._store.load(macro_id)

    def save(self, macro: Macro) -> None:
        self._store.save(macro)
        self.macro_saved.emit(macro.metadata.id)
        self.macro_list_changed.emit()

    def delete(self, macro_id: str) -> None:
        self._store.delete(macro_id)
        self.macro_deleted.emit(macro_id)
        self.macro_list_changed.emit()

    def rename(self, macro_id: str, new_name: str) -> None:
        macro = self._store.load(macro_id)
        macro.metadata.name = new_name
        self._store.save(macro)
        self.macro_list_changed.emit()

    def duplicate(self, macro_id: str) -> Macro:
        dup = self._store.duplicate(macro_id)
        self.macro_list_changed.emit()
        return dup
