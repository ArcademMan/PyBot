"""Glassmorphism theme – color palette, global QSS, blur helper.

Visual design heavily inspired by Lily.
"""

from __future__ import annotations

import sys

# ── Palette ──────────────────────────────────────────────────────
BG = "rgba(25, 25, 35, 200)"
CARD_BG = "rgba(255, 255, 255, 8)"
CARD_BORDER = "rgba(255, 255, 255, 15)"
ACCENT = "#7C5CFC"
ACCENT_HOVER = "#9B82FD"
ACCENT_DIM = "rgba(124, 92, 252, 40)"
TEXT = "#EAEAEA"
TEXT_SEC = "#888888"
SIDEBAR_BG = "rgba(15, 15, 25, 220)"
INPUT_BG = "rgba(255, 255, 255, 6)"
INPUT_BORDER = "rgba(255, 255, 255, 20)"

GREEN = "#4CAF50"
ORANGE = "#FF9800"
RED = "#F44336"

# ── Global QSS ──────────────────────────────────────────────────
STYLESHEET = f"""
/* ── Base ─────────────────────────────────────── */
QWidget {{
    color: {TEXT};
    font-family: "Segoe UI", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 13px;
}}
QMainWindow, #CentralWidget {{
    background: transparent;
}}

/* ── Dialogs ──────────────────────────────────── */
QDialog {{
    background: rgb(25, 25, 35);
    color: {TEXT};
}}
QMessageBox {{
    background: rgb(25, 25, 35);
}}
QMessageBox QLabel {{
    color: {TEXT};
}}
QInputDialog {{
    background: rgb(25, 25, 35);
}}
QInputDialog QLabel {{
    color: {TEXT};
}}

/* ── Scrollbar ────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,30); border-radius: 3px; min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent; height: 6px; border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(255,255,255,30); border-radius: 3px; min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Inputs ───────────────────────────────────── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: {INPUT_BG};
    border: 1px solid {INPUT_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXT};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{
    border: none; width: 28px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_SEC};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: rgb(35, 35, 50);
    border: 1px solid {INPUT_BORDER};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {ACCENT_DIM};
    outline: none;
}}

/* ── Buttons ──────────────────────────────────── */
QPushButton {{
    background: {ACCENT};
    border: none;
    border-radius: 8px;
    padding: 9px 24px;
    color: white;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background: {ACCENT};
}}
QPushButton:disabled {{
    background: rgba(124, 92, 252, 80);
    color: rgba(255,255,255,100);
}}
QPushButton#flatBtn {{
    background: transparent;
    padding: 6px;
}}
QPushButton#flatBtn:hover {{
    background: rgba(255,255,255,10);
}}
QPushButton#dangerBtn {{
    background: {RED};
}}
QPushButton#dangerBtn:hover {{
    background: #E53935;
}}

/* ── Checkbox ─────────────────────────────────── */
QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border: 2px solid {INPUT_BORDER};
    border-radius: 4px;
    background: {INPUT_BG};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Slider ───────────────────────────────────── */
QSlider::groove:horizontal {{
    background: rgba(255,255,255,15); height: 4px; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT}; width: 16px; height: 16px;
    margin: -6px 0; border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT}; border-radius: 2px;
}}

/* ── Table ────────────────────────────────────── */
QTableView {{
    background: transparent;
    border: none;
    gridline-color: rgba(255,255,255,8);
    selection-background-color: {ACCENT_DIM};
    outline: none;
}}
QTableView::item {{
    padding: 6px 10px;
    border: none;
}}
QTableView::item:selected {{
    background: {ACCENT_DIM};
}}
QHeaderView {{
    background: transparent;
    border: none;
}}
QHeaderView::section {{
    background: rgba(255,255,255,6);
    border: none;
    border-bottom: 1px solid rgba(255,255,255,10);
    padding: 8px 10px;
    font-weight: 600;
    color: {TEXT_SEC};
}}

/* ── Tooltip ──────────────────────────────────── */
QToolTip {{
    background: rgb(35, 35, 50);
    border: 1px solid rgba(255,255,255,15);
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT};
}}

/* ── Labels ───────────────────────────────────── */
QLabel#sectionTitle {{
    font-size: 20px; font-weight: 700;
}}
QLabel#secondary {{
    color: {TEXT_SEC}; font-size: 12px;
}}
QLabel#accent {{
    color: {ACCENT}; font-weight: 600;
}}

/* ── Menu ─────────────────────────────────────── */
QMenu {{
    background: rgb(30, 30, 45);
    border: 1px solid rgba(255,255,255,15);
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {ACCENT_DIM};
}}
QMenu::separator {{
    height: 1px;
    background: rgba(255,255,255,10);
    margin: 4px 8px;
}}

/* ── PlainTextEdit ────────────────────────────── */
QPlainTextEdit {{
    background: rgba(0,0,0,60);
    border: 1px solid rgba(255,255,255,15);
    border-radius: 10px;
    padding: 10px;
    font-family: "Cascadia Code", "Consolas", "Ubuntu Mono", "Noto Mono", monospace;
    font-size: 12px;
    color: {TEXT};
    selection-background-color: {ACCENT};
}}
"""


# ── Windows DWM acrylic blur ─────────────────────────────────────
def enable_blur(hwnd: int) -> None:
    """Enable acrylic-like blur behind the window (Windows 10+).

    No-op on Linux/macOS.
    """
    if sys.platform != "win32":
        return

    import ctypes

    class _ACCENT_POLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_int),
            ("AccentFlags", ctypes.c_int),
            ("GradientColor", ctypes.c_uint),
            ("AnimationId", ctypes.c_int),
        ]

    class _WINCOMPATTRDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.POINTER(_ACCENT_POLICY)),
            ("SizeOfData", ctypes.c_size_t),
        ]

    accent = _ACCENT_POLICY()
    accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
    accent.GradientColor = 0xCC191923  # AABBGGRR

    data = _WINCOMPATTRDATA()
    data.Attribute = 19  # WCA_ACCENT_POLICY
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
