# xHelper 2.0 Release

**xHelper 2.0 Release** is a Python/PyQt6 desktop utility for managing Android devices through ADB and fastboot. This release focuses on stabilizing the existing feature set, improving plugin support, and documenting installation and safe usage.

## What changed in xHelper 2.0 Release

- The application metadata and main window title now identify the build as `xHelper 2.0 Release`.
- User configuration is stored in `~/.xhelper_config.json`.
- ADB command construction uses safer argument handling and shared helper methods exposed by the main window.
- Plugin loading is deterministic and isolated: plugins are loaded in sorted order, private `_*.py` files are skipped, and one plugin failure does not stop the others.
- The old early-build warning dialog was replaced with a release information dialog.
- Documentation was updated for the 2.0 release.

## Requirements

- Python 3.10+.
- PyQt6.
- Android Platform Tools (`adb`, `fastboot`) available in `PATH` or configured in `~/.xhelper_config.json`.
- Optional: `scrcpy` for screen mirroring.

## Quick start

```bash
python -m pip install PyQt6
python "xHelper 2.0 Release.py"
```

## Automatic installation

Run the installer from the project root:

```bash
python install_xhelper_2_0.py
```

The installer creates a local virtual environment, installs PyQt6, creates a launcher script, attempts to create a desktop shortcut, and warns if `adb`, `fastboot`, or `scrcpy` are missing from `PATH`.

## Plugin development

Plugins live in `plugins/` and expose a single entry point:

```python
def register(main_window):
    ...
```

Useful public API in xHelper 2.0 Release:

| API | Purpose |
| --- | --- |
| `main_window.tabs` | Add plugin tabs. |
| `main_window.log_message(text)` | Write to the shared log. |
| `main_window.settings` | Access user settings from `~/.xhelper_config.json`. |
| `main_window.adb_executable()` | Get the configured ADB executable. |
| `main_window.fastboot_executable()` | Get the configured fastboot executable. |
| `main_window.get_selected_device_id()` | Get the selected Android device serial. |
| `main_window.build_adb_args(command, device_id)` | Build safe ADB command arguments. |
| `main_window.run_adb_capture(command, timeout=30)` | Run ADB and return `CompletedProcess`. |

Avoid long-running work directly in UI slots. Use `QThread` or background threads and report back through Qt signals.
