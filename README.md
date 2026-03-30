<p align="center">
  <img src="./assets/icon.png" alt="PyBot" width="180">
</p>

<h1 align="center">PyBot</h1>

<p align="center">
  <strong>Macro Recorder & Player – Create your own bot</strong><br>
  Record mouse and keyboard actions, replay them with customizable speed and loops, bind hotkeys to macros.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.12+-yellow" alt="Python">
  <img src="https://img.shields.io/badge/gui-PySide6-green" alt="GUI">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License">
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Record** | Capture mouse movement, clicks, keyboard input with configurable sampling |
| **Playback** | Replay macros with adjustable speed, loop count, and delay between loops |
| **Preview** | Dry-run mode that moves the cursor along the macro path showing action labels without executing inputs |
| **Per-macro hotkeys** | Bind a keyboard shortcut to any macro to launch it instantly |
| **Global hotkeys** | F9 Record, F6 Play, F12 Stop (customizable in settings) |
| **Macro editor** | Edit, reorder, delete individual actions, modify delays and coordinates |
| **Glassmorphism UI** | Modern frameless window with blur, animations, and system tray support |

## Installation

### From source

```bash
git clone https://github.com/arcademman/PyBot.git
cd PyBot
pip install .
python run.py
```

### From release

**Windows:**
1. Download `PyBot_Setup_x.x.x.exe` from [Releases](https://github.com/arcademman/PyBot/releases)
2. Run the installer

**Linux:**
1. Download `PyBot-linux-x64.tar.gz` from [Releases](https://github.com/arcademman/PyBot/releases)
2. Extract and run `./PyBot`

## Build

### Windows (exe + installer)

```bash
pip install ".[dev]"
pyinstaller run.spec
```

This builds the exe in `dist/PyBot/` and automatically generates the Inno Setup installer in `installer_output/`.

### Linux

```bash
pip install ".[dev]"
pyinstaller run.spec
tar -czf PyBot-linux-x64.tar.gz -C dist PyBot
```

Or push a tag to trigger the GitHub Actions workflow:

```bash
git tag v0.x.0
git push --tags
```

## License

[MIT](LICENSE)
