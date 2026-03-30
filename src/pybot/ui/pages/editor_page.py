"""Macro editor page – macro list on the left, action editor on the right."""

from __future__ import annotations

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QStackedWidget,
)
import qtawesome as qta

from pybot.core.enums import ActionType
from pybot.core.models import Action, Macro, MacroMetadata
from pybot.ui.style import ACCENT, ACCENT_DIM, GREEN, ORANGE, RED, TEXT, TEXT_SEC
from pybot.ui.widgets.glass_card import GlassCard


# ── Action table model ────────────────────────────────────────────
class ActionTableModel(QAbstractTableModel):
    COLUMNS = ["#", "Type", "Detail", "Delay (s)"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._actions: list[Action] = []

    def set_actions(self, actions: list[Action]) -> None:
        self.beginResetModel()
        self._actions = actions
        self.endResetModel()

    def actions(self) -> list[Action]:
        return self._actions

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._actions)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        action = self._actions[index.row()]
        match index.column():
            case 0:
                return str(index.row() + 1)
            case 1:
                return action.human_type()
            case 2:
                return action.human_detail()
            case 3:
                return f"{action.delay_before:.3f}"
        return None

    def remove_rows(self, rows: list[int]) -> None:
        for r in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), r, r)
            self._actions.pop(r)
            self.endRemoveRows()

    def move_row(self, from_row: int, to_row: int) -> None:
        if from_row == to_row or from_row < 0 or to_row < 0:
            return
        if to_row > from_row:
            self.beginMoveRows(QModelIndex(), from_row, from_row, QModelIndex(), to_row + 1)
        else:
            self.beginMoveRows(QModelIndex(), from_row, from_row, QModelIndex(), to_row)
        action = self._actions.pop(from_row)
        self._actions.insert(to_row, action)
        self.endMoveRows()

    def flags(self, index):
        default = super().flags(index)
        if index.isValid():
            return default | Qt.ItemFlag.ItemIsDragEnabled
        return default | Qt.ItemFlag.ItemIsDropEnabled


# ── Editor page ───────────────────────────────────────────────────
class EditorPage(QWidget):
    macro_modified = Signal(Macro)
    delete_requested = Signal(str)
    rename_requested = Signal(str, str)
    duplicate_requested = Signal(str)
    play_requested = Signal(str)
    preview_requested = Signal(str)
    hotkey_changed = Signal(str, str)   # macro_id, hotkey
    load_requested = Signal(str)  # macro_id — parent loads and calls load_macro()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._macro: Macro | None = None
        self._macros_cache: dict[str, MacroMetadata] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)

        # ══════════════════════════════════════════
        #  LEFT: Macro list
        # ══════════════════════════════════════════
        left = QVBoxLayout()
        left.setSpacing(8)

        left_title = QLabel("Macro Editor")
        left_title.setObjectName("sectionTitle")
        left.addWidget(left_title)

        left_hint = QLabel("Select a macro to edit")
        left_hint.setObjectName("secondary")
        left.addWidget(left_hint)

        left.addSpacing(4)

        self._macro_list = QListWidget()
        self._macro_list.setStyleSheet(
            "QListWidget {"
            "  background: rgba(255,255,255,5);"
            "  border: 1px solid rgba(255,255,255,10);"
            "  border-radius: 10px;"
            "  padding: 4px;"
            "  outline: none;"
            "}"
            "QListWidget::item {"
            "  padding: 10px 12px;"
            "  border-radius: 6px;"
            "}"
            "QListWidget::item:selected {"
            f"  background: {ACCENT_DIM};"
            "}"
            "QListWidget::item:hover {"
            "  background: rgba(255,255,255,8);"
            "}"
        )
        self._macro_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._macro_list.customContextMenuRequested.connect(self._show_context_menu)
        self._macro_list.currentItemChanged.connect(self._on_macro_selected)
        left.addWidget(self._macro_list, 1)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)

        # ══════════════════════════════════════════
        #  RIGHT: stacked — placeholder / editor
        # ══════════════════════════════════════════
        self._stack = QStackedWidget()

        # Page 0: placeholder
        placeholder = QWidget()
        ph_layout = QVBoxLayout(placeholder)
        ph_layout.addStretch()
        ph_icon = QLabel()
        ph_icon.setPixmap(qta.icon("mdi6.playlist-edit", color=TEXT_SEC).pixmap(64, 64))
        ph_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(ph_icon)
        ph_text = QLabel("Select a macro from the list to start editing")
        ph_text.setObjectName("secondary")
        ph_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_text.setWordWrap(True)
        ph_layout.addWidget(ph_text)
        ph_layout.addStretch()
        self._stack.addWidget(placeholder)

        # Page 1: actual editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(12)

        # ── Header: name + buttons ────────────────
        header = QHBoxLayout()
        header.setSpacing(8)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Macro name")
        self._name_edit.setStyleSheet(
            f"QLineEdit {{ font-size: 16px; font-weight: 600;"
            f"  background: rgba(255,255,255,6); border: 1px solid rgba(255,255,255,20);"
            f"  border-radius: 8px; padding: 8px 12px; color: {TEXT}; }}"
            f"QLineEdit:focus {{ border: 1px solid {ACCENT}; }}"
        )
        header.addWidget(self._name_edit, 1)

        self._save_btn = QPushButton(qta.icon("mdi6.content-save", color="white"), "  Save")
        self._save_btn.setFixedHeight(38)
        self._save_btn.clicked.connect(self._on_save)
        header.addWidget(self._save_btn)

        self._del_macro_btn = QPushButton(qta.icon("mdi6.delete-outline", color="white"), "")
        self._del_macro_btn.setFixedSize(38, 38)
        self._del_macro_btn.setObjectName("dangerBtn")
        self._del_macro_btn.setToolTip("Delete macro")
        self._del_macro_btn.clicked.connect(self._on_delete_macro)
        header.addWidget(self._del_macro_btn)

        editor_layout.addLayout(header)

        # ── Body: table + properties ──────────────
        body = QHBoxLayout()
        body.setSpacing(12)

        # Table
        self._model = ActionTableModel()
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setDragDropMode(QTableView.DragDropMode.InternalMove)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        body.addWidget(self._table, 3)

        # Properties
        props_card = GlassCard()
        props_layout = props_card.body()
        props_layout.setSpacing(10)

        props_title = QLabel("Properties")
        props_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        props_layout.addWidget(props_title)

        self._props_hint = QLabel("Select an action")
        self._props_hint.setObjectName("secondary")
        props_layout.addWidget(self._props_hint)

        form = QFormLayout()
        form.setSpacing(8)

        self._prop_type = QLabel("-")
        self._prop_type.setObjectName("accent")
        form.addRow("Type", self._prop_type)

        self._prop_key = QLineEdit()
        self._prop_key.setPlaceholderText("key")
        form.addRow("Key", self._prop_key)

        self._prop_x = QSpinBox()
        self._prop_x.setRange(-99999, 99999)
        form.addRow("X", self._prop_x)

        self._prop_y = QSpinBox()
        self._prop_y.setRange(-99999, 99999)
        form.addRow("Y", self._prop_y)

        self._prop_button = QComboBox()
        self._prop_button.addItems(["left", "right", "middle"])
        form.addRow("Button", self._prop_button)

        self._prop_delay = QDoubleSpinBox()
        self._prop_delay.setRange(0.0, 9999.0)
        self._prop_delay.setDecimals(3)
        self._prop_delay.setSingleStep(0.01)
        self._prop_delay.setSuffix("s")
        form.addRow("Delay", self._prop_delay)

        # Store form rows for show/hide
        self._form = form
        self._form_widgets = {
            "key": (form.labelForField(self._prop_key), self._prop_key),
            "x": (form.labelForField(self._prop_x), self._prop_x),
            "y": (form.labelForField(self._prop_y), self._prop_y),
            "button": (form.labelForField(self._prop_button), self._prop_button),
        }

        props_layout.addLayout(form)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedHeight(36)
        apply_btn.clicked.connect(self._apply_properties)
        props_layout.addWidget(apply_btn)

        props_layout.addStretch()

        # Action toolbar
        tool_row = QHBoxLayout()
        for icon, tip, slot in [
            ("mdi6.delete-outline", "Delete selected", self._delete_selected),
            ("mdi6.arrow-up", "Move up", self._move_up),
            ("mdi6.arrow-down", "Move down", self._move_down),
        ]:
            btn = QPushButton(qta.icon(icon, color=RED if "delete" in icon else "#EAEAEA"), "")
            btn.setFixedSize(36, 36)
            btn.setObjectName("flatBtn")
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            tool_row.addWidget(btn)
        tool_row.addStretch()
        props_layout.addLayout(tool_row)

        body.addWidget(props_card, 1)
        editor_layout.addLayout(body, 1)

        # Action count
        self._count_label = QLabel("")
        self._count_label.setObjectName("secondary")
        editor_layout.addWidget(self._count_label)

        self._stack.addWidget(editor_widget)

        # ══════════════════════════════════════════
        root.addWidget(left_widget)
        root.addWidget(self._stack, 1)

        # Start with no action selected
        self._hide_all_props()

    # ── Public API ────────────────────────────────
    def refresh_macro_list(self, macros: list[MacroMetadata]) -> None:
        self._macros_cache = {m.id: m for m in macros}
        current_id = None
        item = self._macro_list.currentItem()
        if item:
            current_id = item.data(Qt.ItemDataRole.UserRole)

        self._macro_list.blockSignals(True)
        self._macro_list.clear()
        select_idx = -1
        for i, m in enumerate(macros):
            label = f"{m.name}  [{m.hotkey}]" if m.hotkey else m.name
            it = QListWidgetItem(label)
            it.setData(Qt.ItemDataRole.UserRole, m.id)
            it.setData(Qt.ItemDataRole.UserRole + 1, m.hotkey or "")
            self._macro_list.addItem(it)
            if m.id == current_id:
                select_idx = i
        self._macro_list.blockSignals(False)

        if select_idx >= 0:
            self._macro_list.setCurrentRow(select_idx)

    def load_macro(self, macro: Macro) -> None:
        """Load a macro into the editor (called externally, e.g. from record page)."""
        self._macro = macro
        self._name_edit.setText(macro.name)
        self._model.set_actions(list(macro.actions))
        self._update_count()
        self._stack.setCurrentIndex(1)
        self._hide_all_props()
        # Select it in the list
        for i in range(self._macro_list.count()):
            item = self._macro_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == macro.metadata.id:
                self._macro_list.blockSignals(True)
                self._macro_list.setCurrentRow(i)
                self._macro_list.blockSignals(False)
                break

    # ── Private: macro list ───────────────────────
    def _show_context_menu(self, pos) -> None:
        item = self._macro_list.itemAt(pos)
        if not item:
            return
        mid = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        play_act = menu.addAction(qta.icon("mdi6.play", color=GREEN), "Play")
        preview_act = menu.addAction(qta.icon("mdi6.eye-outline", color=ORANGE), "Preview")
        menu.addSeparator()
        rename_act = menu.addAction("Rename")
        dup_act = menu.addAction("Duplicate")
        menu.addSeparator()
        current_hotkey = item.data(Qt.ItemDataRole.UserRole + 1) or ""
        if current_hotkey:
            hotkey_act = menu.addAction(
                qta.icon("mdi6.keyboard-outline", color=ACCENT),
                f"Change Hotkey ({current_hotkey})",
            )
            unbind_act = menu.addAction("Unbind Hotkey")
        else:
            hotkey_act = menu.addAction(
                qta.icon("mdi6.keyboard-outline", color=ACCENT), "Bind Hotkey"
            )
            unbind_act = None
        menu.addSeparator()
        del_act = menu.addAction(qta.icon("mdi6.delete-outline", color=RED), "Delete")

        action = menu.exec(self._macro_list.mapToGlobal(pos))
        if action == play_act:
            self.play_requested.emit(mid)
        elif action == preview_act:
            self.preview_requested.emit(mid)
        elif action == rename_act:
            name, ok = QInputDialog.getText(self, "Rename", "New name:", text=item.text())
            if ok and name.strip():
                self.rename_requested.emit(mid, name.strip())
        elif action == dup_act:
            self.duplicate_requested.emit(mid)
        elif action == hotkey_act:
            key, ok = QInputDialog.getText(
                self, "Bind Hotkey",
                "Enter hotkey (e.g. ctrl+F1, F7, alt+shift+1):",
                text=current_hotkey,
            )
            if ok:
                self.hotkey_changed.emit(mid, key.strip())
        elif unbind_act and action == unbind_act:
            self.hotkey_changed.emit(mid, "")
        elif action == del_act:
            if QMessageBox.question(self, "Delete", f'Delete "{item.text()}"?') == QMessageBox.StandardButton.Yes:
                self.delete_requested.emit(mid)

    def _on_macro_selected(self, current: QListWidgetItem | None, previous) -> None:
        if not current:
            self._stack.setCurrentIndex(0)
            return
        mid = current.data(Qt.ItemDataRole.UserRole)
        self.load_requested.emit(mid)

    # ── Private: properties ───────────────────────
    def _on_selection_changed(self) -> None:
        rows = self._selected_rows()
        if len(rows) != 1:
            self._hide_all_props()
            return

        action = self._model.actions()[rows[0]]
        self._props_hint.hide()
        self._prop_type.setText(action.human_type())
        self._prop_delay.setValue(action.delay_before)

        # Show only relevant fields
        is_key = action.type in (ActionType.KEY_PRESS, ActionType.KEY_RELEASE)
        is_mouse = action.type in (
            ActionType.MOUSE_CLICK, ActionType.MOUSE_RELEASE,
            ActionType.MOUSE_MOVE, ActionType.MOUSE_SCROLL,
        )
        has_button = action.type in (ActionType.MOUSE_CLICK, ActionType.MOUSE_RELEASE)

        for name, (label, widget) in self._form_widgets.items():
            if name == "key":
                label.setVisible(is_key)
                widget.setVisible(is_key)
            elif name in ("x", "y"):
                label.setVisible(is_mouse)
                widget.setVisible(is_mouse)
            elif name == "button":
                label.setVisible(has_button)
                widget.setVisible(has_button)

        if is_key:
            self._prop_key.setText(action.key or "")
        if is_mouse:
            self._prop_x.setValue(action.x or 0)
            self._prop_y.setValue(action.y or 0)
        if has_button and action.button:
            idx = self._prop_button.findText(action.button)
            if idx >= 0:
                self._prop_button.setCurrentIndex(idx)

    def _hide_all_props(self) -> None:
        self._props_hint.show()
        self._props_hint.setText("Select an action")
        self._prop_type.setText("-")
        for label, widget in self._form_widgets.values():
            label.setVisible(False)
            widget.setVisible(False)

    def _apply_properties(self) -> None:
        rows = self._selected_rows()
        if len(rows) != 1:
            return
        action = self._model.actions()[rows[0]]
        if self._prop_key.isVisible():
            action.key = self._prop_key.text() or None
        if self._prop_x.isVisible():
            action.x = self._prop_x.value()
        if self._prop_y.isVisible():
            action.y = self._prop_y.value()
        if self._prop_button.isVisible():
            action.button = self._prop_button.currentText()
        action.delay_before = self._prop_delay.value()
        self._model.dataChanged.emit(
            self._model.index(rows[0], 0),
            self._model.index(rows[0], self._model.columnCount() - 1),
        )

    # ── Private: action manipulation ──────────────
    def _delete_selected(self) -> None:
        rows = self._selected_rows()
        if rows:
            self._model.remove_rows(rows)
            self._update_count()

    def _move_up(self) -> None:
        rows = self._selected_rows()
        if len(rows) == 1 and rows[0] > 0:
            self._model.move_row(rows[0], rows[0] - 1)
            self._table.selectRow(rows[0] - 1)

    def _move_down(self) -> None:
        rows = self._selected_rows()
        if len(rows) == 1 and rows[0] < self._model.rowCount() - 1:
            self._model.move_row(rows[0], rows[0] + 1)
            self._table.selectRow(rows[0] + 1)

    def _on_save(self) -> None:
        if self._macro:
            new_name = self._name_edit.text().strip()
            if new_name and new_name != self._macro.name:
                self._macro.metadata.name = new_name
                self.rename_requested.emit(self._macro.metadata.id, new_name)
            self._macro.actions = self._model.actions()
            self.macro_modified.emit(self._macro)

    def _on_delete_macro(self) -> None:
        if not self._macro:
            return
        if QMessageBox.question(
            self, "Delete", f'Delete "{self._macro.name}"?'
        ) == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self._macro.metadata.id)
            self._macro = None
            self._stack.setCurrentIndex(0)

    def _update_count(self) -> None:
        n = self._model.rowCount()
        self._count_label.setText(f"{n} action{'s' if n != 1 else ''}")

    def _selected_rows(self) -> list[int]:
        return sorted({idx.row() for idx in self._table.selectionModel().selectedRows()})
