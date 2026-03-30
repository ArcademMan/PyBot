"""Frameless main window with sidebar, animated stack, and title bar."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from pybot.core.enums import PlaybackState, RecordingState
from pybot.core.models import Macro, PlaybackConfig
from pybot.core.paths import ensure_dirs
from pybot.core.settings import AppSettings
from pybot.core.hotkey_manager import HotkeyManager
from pybot.services.macro_service import MacroService
from pybot.services.playback_service import PlaybackService
from pybot.services.recording_service import RecordingService
from pybot.ui.pages.editor_page import EditorPage
from pybot.ui.pages.record_page import RecordPage
from pybot.ui.pages.settings_page import SettingsPage
from pybot.ui.style import enable_blur
from pybot.ui.widgets.animated_stack import AnimatedStack
from pybot.ui.widgets.sidebar import Sidebar
from pybot.ui.widgets.title_bar import TitleBar
from pybot.ui.widgets.toast import show_toast
from pybot.ui.widgets.tray_icon import TrayIcon


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(900, 600)
        self.resize(1000, 660)
        self.setWindowTitle("PyBot")

        # ── Init paths ────────────────────────
        ensure_dirs()

        # ── Services ──────────────────────────
        self._settings = AppSettings.load()
        self._macro_service = MacroService(parent=self)
        self._recording_service = RecordingService(parent=self)
        self._playback_service = PlaybackService(parent=self)
        self._hotkey_manager = HotkeyManager()

        # ── Central widget ────────────────────
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Title bar
        self._title_bar = TitleBar(self)
        outer.addWidget(self._title_bar)

        # Body: sidebar + pages
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._sidebar = Sidebar()
        body.addWidget(self._sidebar)

        self._stack = AnimatedStack()
        body.addWidget(self._stack, 1)

        outer.addLayout(body, 1)

        # ── Pages ─────────────────────────────
        self._record_page = RecordPage()
        self._editor_page = EditorPage()
        self._settings_page = SettingsPage()

        self._stack.addWidget(self._record_page)
        self._stack.addWidget(self._editor_page)
        self._stack.addWidget(self._settings_page)

        self._sidebar.set_active(0)

        # ── Load settings into UI ─────────────
        self._settings_page.load_settings(self._settings)

        # ── Tray icon ─────────────────────────
        self._tray = TrayIcon(self)
        self._tray.show()

        # ── Connect signals ───────────────────
        self._connect_signals()
        self._setup_hotkeys()
        self._refresh_macro_list()

    # ── Paint background ──────────────────────
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        p.setClipPath(path)
        p.fillRect(self.rect(), QColor(25, 25, 35, 200))
        p.end()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        try:
            enable_blur(int(self.winId()))
        except Exception:
            pass

    def closeEvent(self, event) -> None:
        if self._settings.minimize_to_tray and self._tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self._hotkey_manager.stop()
            event.accept()

    # ── Signal wiring ─────────────────────────
    def _connect_signals(self) -> None:
        # Sidebar
        self._sidebar.page_requested.connect(self._stack.fade_to)

        # Recording
        self._record_page.record_toggled.connect(self._toggle_recording)
        self._recording_service.state_changed.connect(self._record_page.set_recording_state)
        self._recording_service.recording_finished.connect(self._on_recording_finished)

        # Playback
        self._record_page.play_requested.connect(self._play_macro)
        self._record_page.stop_requested.connect(self._playback_service.stop)
        self._playback_service.state_changed.connect(self._record_page.set_playback_state)

        # Macro management
        self._record_page.delete_requested.connect(self._delete_macro)
        self._record_page.rename_requested.connect(self._rename_macro)
        self._record_page.duplicate_requested.connect(self._duplicate_macro)
        self._record_page.edit_requested.connect(self._open_editor)
        self._macro_service.macro_list_changed.connect(self._refresh_macro_list)

        # Editor
        self._editor_page.macro_modified.connect(self._save_macro)
        self._editor_page.delete_requested.connect(self._delete_macro)
        self._editor_page.rename_requested.connect(self._rename_macro)
        self._editor_page.load_requested.connect(self._load_macro_into_editor)

        # Settings
        self._settings_page.settings_saved.connect(self._on_settings_saved)

    # ── Hotkeys ───────────────────────────────
    def _setup_hotkeys(self) -> None:
        self._hotkey_manager.register(self._settings.hotkey_record, self._toggle_recording)
        self._hotkey_manager.register(self._settings.hotkey_play, self._play_selected)
        self._hotkey_manager.register(self._settings.hotkey_stop, self._emergency_stop)
        self._hotkey_manager.start()

    # ── Actions ───────────────────────────────
    def _toggle_recording(self) -> None:
        self._recording_service.toggle(
            record_movement=self._record_page.record_mouse_movement,
            record_clicks=self._record_page.record_mouse_clicks,
            record_keyboard=self._record_page.record_keyboard,
            sample_ms=self._settings.mouse_sample_interval_ms,
        )

    def _on_recording_finished(self, macro: Macro) -> None:
        self._macro_service.save(macro)
        self._refresh_macro_list()
        show_toast(self, f"Macro saved ({macro.action_count} actions)", "success")

    def _play_macro(self, macro_id: str) -> None:
        try:
            macro = self._macro_service.load(macro_id)
        except Exception:
            return
        config = PlaybackConfig(
            speed_multiplier=self._record_page.speed,
            loop_count=self._record_page.loops,
            delay_between_loops=self._record_page.delay_between_loops,
        )
        self._playback_service.play(macro, config)

    def _play_selected(self) -> None:
        mid = self._record_page.selected_macro_id()
        if mid:
            self._play_macro(mid)

    def _emergency_stop(self) -> None:
        if self._playback_service.is_playing:
            self._playback_service.stop()
        if self._recording_service.is_recording:
            self._recording_service.stop()

    def _delete_macro(self, macro_id: str) -> None:
        self._macro_service.delete(macro_id)
        show_toast(self, "Macro deleted", "info")

    def _rename_macro(self, macro_id: str, new_name: str) -> None:
        self._macro_service.rename(macro_id, new_name)
        show_toast(self, f"Renamed to \"{new_name}\"", "success")

    def _duplicate_macro(self, macro_id: str) -> None:
        self._macro_service.duplicate(macro_id)
        show_toast(self, "Macro duplicated", "success")

    def _open_editor(self, macro_id: str) -> None:
        try:
            macro = self._macro_service.load(macro_id)
        except Exception:
            return
        self._editor_page.load_macro(macro)
        self._stack.fade_to(1)
        self._sidebar.set_active(1)

    def _save_macro(self, macro: Macro) -> None:
        self._macro_service.save(macro)
        show_toast(self, "Macro saved", "success")

    def _load_macro_into_editor(self, macro_id: str) -> None:
        try:
            macro = self._macro_service.load(macro_id)
        except Exception:
            return
        self._editor_page.load_macro(macro)

    def _refresh_macro_list(self) -> None:
        macros = self._macro_service.list_macros()
        self._record_page.refresh_macro_list(macros)
        self._editor_page.refresh_macro_list(macros)

    def _on_settings_saved(self, settings: AppSettings) -> None:
        self._settings = settings
        self._hotkey_manager.stop()
        self._hotkey_manager = HotkeyManager()
        self._setup_hotkeys()
        show_toast(self, "Settings saved", "success")
