"""Home / Record page – main state indicator, controls, macro list."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMenu,
    QInputDialog,
    QMessageBox,
    QDoubleSpinBox,
    QSpinBox,
)
import qtawesome as qta

from pybot.core.enums import PlaybackState, RecordingState
from pybot.core.models import MacroMetadata
from pybot.ui.style import ACCENT, ACCENT_DIM, GREEN, ORANGE, RED, TEXT, TEXT_SEC
from pybot.ui.widgets.glass_card import GlassCard
from pybot.ui.widgets.state_indicator import StateIndicator


class RecordPage(QWidget):
    # Signals to parent
    record_toggled = Signal()
    play_requested = Signal(str)        # macro_id
    stop_requested = Signal()
    delete_requested = Signal(str)      # macro_id
    rename_requested = Signal(str, str) # macro_id, new_name
    duplicate_requested = Signal(str)   # macro_id
    edit_requested = Signal(str)        # macro_id
    preview_requested = Signal(str)     # macro_id
    hotkey_changed = Signal(str, str)   # macro_id, hotkey (empty = unbind)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)

        # ── Left: state + controls ────────────────
        left = QVBoxLayout()
        left.setSpacing(12)

        left.addSpacing(4)

        left.addSpacing(8)

        # State indicator
        self._indicator = StateIndicator()
        left.addWidget(self._indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

        # State label
        self._state_label = QLabel("Idle")
        self._state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._state_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {ACCENT};")
        left.addWidget(self._state_label)

        # Selected macro label
        self._selected_label = QLabel("No macro selected")
        self._selected_label.setObjectName("secondary")
        self._selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(self._selected_label)

        # Hotkey hint
        hint = QLabel("F9 Record  \u2022  F6 Play  \u2022  F12 Stop")
        hint.setObjectName("secondary")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(hint)

        left.addSpacing(8)

        # Control buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._rec_btn = QPushButton(qta.icon("mdi6.record-circle-outline", color="white"), "  Record")
        self._rec_btn.setFixedHeight(42)
        self._rec_btn.clicked.connect(self.record_toggled.emit)
        btn_row.addWidget(self._rec_btn)

        self._preview_btn = QPushButton(qta.icon("mdi6.eye-outline", color="white"), "  Preview")
        self._preview_btn.setFixedHeight(42)
        self._preview_btn.setStyleSheet(
            f"QPushButton {{ background: {ORANGE}; border: none; border-radius: 8px;"
            f"  padding: 9px 24px; color: white; font-weight: 600; }}"
            f"QPushButton:hover {{ background: #FFB74D; }}"
            f"QPushButton:disabled {{ background: rgba(255,152,0,80); color: rgba(255,255,255,100); }}"
        )
        self._preview_btn.clicked.connect(self._on_preview_clicked)
        btn_row.addWidget(self._preview_btn)

        self._play_btn = QPushButton(qta.icon("mdi6.play", color="white"), "  Play")
        self._play_btn.setFixedHeight(42)
        self._play_btn.setStyleSheet(
            f"QPushButton {{ background: {GREEN}; border: none; border-radius: 8px;"
            f"  padding: 9px 24px; color: white; font-weight: 600; }}"
            f"QPushButton:hover {{ background: #66BB6A; }}"
            f"QPushButton:disabled {{ background: rgba(76,175,80,80); color: rgba(255,255,255,100); }}"
        )
        self._play_btn.clicked.connect(self._on_play_clicked)
        btn_row.addWidget(self._play_btn)

        self._stop_btn = QPushButton(qta.icon("mdi6.stop", color="white"), "  Stop")
        self._stop_btn.setFixedHeight(42)
        self._stop_btn.setStyleSheet(
            f"QPushButton {{ background: {RED}; border: none; border-radius: 8px;"
            f"  padding: 9px 24px; color: white; font-weight: 600; }}"
            f"QPushButton:hover {{ background: #E53935; }}"
        )
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        btn_row.addWidget(self._stop_btn)

        left.addLayout(btn_row)

        # Recording options
        rec_card = GlassCard()
        rec_layout = rec_card.body()
        rec_layout.setSpacing(6)

        self._chk_mouse_move = QCheckBox("Record mouse movement")
        self._chk_mouse_move.setChecked(True)
        rec_layout.addWidget(self._chk_mouse_move)

        self._chk_mouse_click = QCheckBox("Record mouse clicks")
        self._chk_mouse_click.setChecked(True)
        rec_layout.addWidget(self._chk_mouse_click)

        self._chk_keyboard = QCheckBox("Record keyboard")
        self._chk_keyboard.setChecked(True)
        rec_layout.addWidget(self._chk_keyboard)

        left.addWidget(rec_card)

        # Playback config
        config_card = GlassCard()
        cfg_layout = config_card.body()

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed"))
        self._speed_spin = QDoubleSpinBox()
        self._speed_spin.setRange(0.1, 10.0)
        self._speed_spin.setSingleStep(0.25)
        self._speed_spin.setValue(1.0)
        self._speed_spin.setSuffix("x")
        self._speed_spin.setFixedWidth(90)
        speed_row.addStretch()
        speed_row.addWidget(self._speed_spin)
        cfg_layout.addLayout(speed_row)

        loop_row = QHBoxLayout()
        loop_row.addWidget(QLabel("Loops"))
        self._loop_spin = QSpinBox()
        self._loop_spin.setRange(0, 9999)
        self._loop_spin.setValue(1)
        self._loop_spin.setSpecialValueText("\u221e")
        self._loop_spin.setFixedWidth(90)
        loop_row.addStretch()
        loop_row.addWidget(self._loop_spin)
        cfg_layout.addLayout(loop_row)

        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Delay between loops"))
        self._delay_spin = QDoubleSpinBox()
        self._delay_spin.setRange(0.0, 60.0)
        self._delay_spin.setSingleStep(0.5)
        self._delay_spin.setValue(0.0)
        self._delay_spin.setSuffix("s")
        self._delay_spin.setFixedWidth(90)
        delay_row.addStretch()
        delay_row.addWidget(self._delay_spin)
        cfg_layout.addLayout(delay_row)

        left.addWidget(config_card)
        left.addStretch()

        root.addLayout(left, 3)

        # ── Right: macro list ─────────────────────
        right = QVBoxLayout()
        right.setSpacing(8)

        list_header = QHBoxLayout()
        list_title = QLabel("Saved Macros")
        list_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        list_header.addWidget(list_title)
        list_header.addStretch()

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
        self._macro_list.itemDoubleClicked.connect(self._on_double_click)
        self._macro_list.currentItemChanged.connect(self._on_selection_changed)

        right.addLayout(list_header)
        right.addWidget(self._macro_list, 1)

        root.addLayout(right, 2)

    # ── Public API ────────────────────────────────
    def refresh_macro_list(self, macros: list[MacroMetadata]) -> None:
        self._macro_list.clear()
        for m in macros:
            label = f"{m.name}  [{m.hotkey}]" if m.hotkey else m.name
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, m.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, m.hotkey or "")
            self._macro_list.addItem(item)

    def set_recording_state(self, state: RecordingState) -> None:
        if state == RecordingState.RECORDING:
            self._indicator.set_state("recording")
            self._state_label.setText("Recording...")
            self._state_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {RED};")
            self._rec_btn.setText("  Stop Rec")
        else:
            self._indicator.set_state("idle")
            self._state_label.setText("Idle")
            self._state_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {ACCENT};")
            self._rec_btn.setText("  Record")

    def set_playback_state(self, state: PlaybackState) -> None:
        if state == PlaybackState.PLAYING:
            self._indicator.set_state("playing")
            self._state_label.setText("Playing...")
            self._state_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {GREEN};")
        elif state == PlaybackState.IDLE:
            self._indicator.set_state("idle")
            self._state_label.setText("Idle")
            self._state_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {ACCENT};")

    @property
    def speed(self) -> float:
        return self._speed_spin.value()

    @property
    def loops(self) -> int:
        return self._loop_spin.value()

    @property
    def delay_between_loops(self) -> float:
        return self._delay_spin.value()

    @property
    def record_mouse_movement(self) -> bool:
        return self._chk_mouse_move.isChecked()

    @property
    def record_mouse_clicks(self) -> bool:
        return self._chk_mouse_click.isChecked()

    @property
    def record_keyboard(self) -> bool:
        return self._chk_keyboard.isChecked()

    def selected_macro_id(self) -> str | None:
        item = self._macro_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    # ── Private ───────────────────────────────────
    def _on_selection_changed(self, current: QListWidgetItem | None, previous) -> None:
        if current:
            self._selected_label.setText(f"Loaded: {current.text()}")
            self._selected_label.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: 600;")
        else:
            self._selected_label.setText("No macro selected")
            self._selected_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")

    def _on_preview_clicked(self) -> None:
        mid = self.selected_macro_id()
        if mid:
            self.preview_requested.emit(mid)

    def _on_play_clicked(self) -> None:
        mid = self.selected_macro_id()
        if mid:
            self.play_requested.emit(mid)

    def _on_double_click(self, item: QListWidgetItem) -> None:
        mid = item.data(Qt.ItemDataRole.UserRole)
        if mid:
            self.edit_requested.emit(mid)

    def _show_context_menu(self, pos) -> None:
        item = self._macro_list.itemAt(pos)
        if not item:
            return
        mid = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        play_act = menu.addAction(qta.icon("mdi6.play", color=GREEN), "Play")
        preview_act = menu.addAction(qta.icon("mdi6.eye-outline", color=ORANGE), "Preview")
        edit_act = menu.addAction(qta.icon("mdi6.pencil-outline", color=TEXT), "Edit")
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
        elif action == edit_act:
            self.edit_requested.emit(mid)
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
            if QMessageBox.question(self, "Delete", f"Delete \"{item.text()}\"?") == QMessageBox.StandardButton.Yes:
                self.delete_requested.emit(mid)
