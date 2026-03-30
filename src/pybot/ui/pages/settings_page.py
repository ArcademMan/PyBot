"""Settings page – hotkeys, recording, playback, general."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pybot.core.settings import AppSettings
from pybot.ui.widgets.glass_card import GlassCard


class SettingsPage(QWidget):
    settings_saved = Signal(AppSettings)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)

        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self._save_btn = QPushButton("Save")
        self._save_btn.setFixedHeight(36)
        self._save_btn.clicked.connect(self._on_save)
        header.addWidget(self._save_btn)

        root.addLayout(header)
        root.addSpacing(12)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }"
                             "QScrollArea > QWidget > QWidget { background: transparent; }")
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QVBoxLayout(container)
        form.setSpacing(16)
        form.setContentsMargins(0, 0, 8, 0)

        # ── Hotkeys ───────────────────────────
        form.addWidget(self._section_label("Hotkeys"))
        card = GlassCard()
        cl = card.body()
        cl.setSpacing(10)

        self._hk_record = QLineEdit("F9")
        cl.addLayout(self._row("Record", self._hk_record))

        self._hk_play = QLineEdit("F6")
        cl.addLayout(self._row("Play", self._hk_play))

        self._hk_stop = QLineEdit("F12")
        cl.addLayout(self._row("Emergency stop", self._hk_stop))

        form.addWidget(card)

        # ── Recording ─────────────────────────
        form.addWidget(self._section_label("Recording"))
        card2 = GlassCard()
        cl2 = card2.body()
        cl2.setSpacing(10)

        self._rec_mouse_move = QCheckBox("Record mouse movement")
        self._rec_mouse_move.setChecked(True)
        cl2.addWidget(self._rec_mouse_move)

        self._sample_ms = QSpinBox()
        self._sample_ms.setRange(5, 200)
        self._sample_ms.setValue(20)
        self._sample_ms.setSuffix(" ms")
        cl2.addLayout(self._row("Mouse sample interval", self._sample_ms))

        form.addWidget(card2)

        # ── Playback ─────────────────────────
        form.addWidget(self._section_label("Playback"))
        card3 = GlassCard()
        cl3 = card3.body()
        cl3.setSpacing(10)

        self._default_speed = QDoubleSpinBox()
        self._default_speed.setRange(0.1, 10.0)
        self._default_speed.setSingleStep(0.25)
        self._default_speed.setValue(1.0)
        self._default_speed.setSuffix("x")
        cl3.addLayout(self._row("Default speed", self._default_speed))

        self._default_loops = QSpinBox()
        self._default_loops.setRange(0, 9999)
        self._default_loops.setValue(1)
        self._default_loops.setSpecialValueText("\u221e")
        cl3.addLayout(self._row("Default loops", self._default_loops))

        form.addWidget(card3)

        # ── General ──────────────────────────
        form.addWidget(self._section_label("General"))
        card4 = GlassCard()
        cl4 = card4.body()
        cl4.setSpacing(10)

        self._minimize_tray = QCheckBox("Minimize to tray on close")
        self._minimize_tray.setChecked(True)
        cl4.addWidget(self._minimize_tray)

        self._start_minimized = QCheckBox("Start minimized")
        cl4.addWidget(self._start_minimized)

        form.addWidget(card4)

        form.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    def load_settings(self, s: AppSettings) -> None:
        self._hk_record.setText(s.hotkey_record)
        self._hk_play.setText(s.hotkey_play)
        self._hk_stop.setText(s.hotkey_stop)
        self._rec_mouse_move.setChecked(s.record_mouse_movement)
        self._sample_ms.setValue(s.mouse_sample_interval_ms)
        self._default_speed.setValue(s.default_speed)
        self._default_loops.setValue(s.default_loops)
        self._minimize_tray.setChecked(s.minimize_to_tray)
        self._start_minimized.setChecked(s.start_minimized)

    def _on_save(self) -> None:
        s = AppSettings(
            hotkey_record=self._hk_record.text(),
            hotkey_play=self._hk_play.text(),
            hotkey_stop=self._hk_stop.text(),
            record_mouse_movement=self._rec_mouse_move.isChecked(),
            mouse_sample_interval_ms=self._sample_ms.value(),
            default_speed=self._default_speed.value(),
            default_loops=self._default_loops.value(),
            minimize_to_tray=self._minimize_tray.isChecked(),
            start_minimized=self._start_minimized.isChecked(),
        )
        s.save()
        self.settings_saved.emit(s)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #888888; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        return lbl

    @staticmethod
    def _row(label_text: str, widget) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        row.addWidget(lbl)
        row.addStretch()
        widget.setFixedWidth(120)
        row.addWidget(widget)
        return row
