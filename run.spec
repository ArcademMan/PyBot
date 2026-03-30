# -*- mode: python ; coding: utf-8 -*-

import os
import platform
import subprocess
import sys

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
ASSETS = os.path.join(ROOT, "assets")

# ── Platform-specific settings ───────────────────
if IS_WINDOWS:
    ICON = os.path.join(ASSETS, "icon.ico")
    HIDDEN = ["pynput.keyboard._win32", "pynput.mouse._win32"]
    CONSOLE = False
else:
    ICON = os.path.join(ASSETS, "icon.png")
    HIDDEN = ["pynput.keyboard._xorg", "pynput.mouse._xorg"]
    CONSOLE = False

# ── Data files ───────────────────────────────────
datas = [
    (os.path.join(ASSETS, "icon.png"), "assets"),
    (os.path.join(ASSETS, "styles"), os.path.join("assets", "styles")),
    (os.path.join(ASSETS, "icons"), os.path.join("assets", "icons")),
]
if IS_WINDOWS:
    datas.append((os.path.join(ASSETS, "icon.ico"), "assets"))

# ── Analysis ─────────────────────────────────────
a = Analysis(
    ["run.py"],
    pathex=[os.path.join(ROOT, "src")],
    binaries=[],
    datas=datas,
    hiddenimports=HIDDEN,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# ── EXE ──────────────────────────────────────────
exe_kwargs = dict(
    exclude_binaries=True,
    name="PyBot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=IS_LINUX,
    upx=True,
    console=CONSOLE,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
if IS_WINDOWS:
    exe_kwargs["icon"] = ICON

exe = EXE(pyz, a.scripts, [], **exe_kwargs)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=IS_LINUX,
    upx=True,
    upx_exclude=[],
    name="PyBot",
)

# ── Windows only: Inno Setup installer ───────────
if IS_WINDOWS:
    ISCC = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ISS = os.path.join(ROOT, "installer.iss")
    if os.path.isfile(ISCC) and os.path.isdir(os.path.join(ROOT, "dist", "PyBot")):
        print("\n[Inno Setup] Creazione installer...")
        ret = subprocess.run([ISCC, ISS], cwd=ROOT)
        if ret.returncode == 0:
            print("[OK] Installer creato in installer_output/")
        else:
            print("[ERRORE] Inno Setup fallito", file=sys.stderr)
