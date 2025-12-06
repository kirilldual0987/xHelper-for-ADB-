**⚠️ Alpha version**  
The program **xHelper α (1.0.1 LTS/ATS)** is in an *alpha* stage. This means it may contain:

- Unfinished / un‑debugged functions.  
- Unexpected crashes when working with ADB/fastboot.  
- Incorrect answers from the device.  
- UI failures if several heavy operations run at the same time.  

We strongly recommend using this build **only for testing** and **not in critical projects**.

---

## 📚 Brief guide to using **xHelper**

*(Functionality is described without using plugins – which is probably impossible because xHelper ships with plugins.)*

| Feature | How to use |
|---------|-------------|
| **Device connection** | Open the **Devices** tab and click **Refresh device list**. Make sure the ADB driver is installed. |
| **Application management** | In the **APK** tab you can **install**, **uninstall**, or **launch** an app by specifying its package name. |
| **Batch installation** | The **Batch APK install** tab lets you choose a folder with several *.apk* files and install them with a single command. |
| **File operations** | The **Files** tab copies files **to** / **from** the device (adb push / pull). |
| **Application testing** | The **App testing** tab runs each app, collects *logcat* and marks the apps that crashed. |
| **Screencast & screenshots** | In the **Device screen** tab you can launch *scrcpy* (if installed) or take a screenshot. |
| **Backups** | The **Backup / Restore** tab creates a full ADB backup and allows you to restore it. |

---

## 🔧 How to write your own plugins for **xHelper**

A **plugin** is just a regular Python module placed in the `plugins/` directory next to `main.py`.  
When the program starts, `XHelperMainWindow.load_plugins()` automatically imports every `*.py` file, searches for a function `register(main_window)`, and calls it, passing the main‑window object.

### Minimal plugin template

```python
# -- coding: utf-8 --
def register(main_window):
    """Register the plugin with the main window."""
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.addWidget(QLabel("Example plugin"))
    main_window.tabs.addTab(tab, "Example")
```

### What you can do inside `register`

| Object / Method | What it does | Example |
|-----------------|----------------|---------|
| `main_window.run_adb_command(...)` | Execute any ADB command. | `main_window.run_adb_command("shell getprop ro.build.version.release")` |
| `main_window.log_message(...)` | Write a line to the right‑hand console log. | `main_window.log_message("[MyPlugin] Started")` |
| `main_window.tabs` | The `QTabWidget` that holds the main tabs. | `main_window.tabs.addTab(my_widget, "My Tab")` |
| `main_window.addDockWidget(area, widget)` | Add a `QDockWidget` (left/right/top/bottom). | `main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)` |
| `main_window.statusBar()` | Access the status bar (`QStatusBar`). | `main_window.statusBar().showMessage("Plugin ready")` |
| `main_window.settings` | Dictionary with user settings (saved in `~/.xhelper_prealpha_config.json`). | `if main_window.settings.get("theme_dark"): …` |
| `main_window.progress_signal` | `pyqtSignal(int)` – useful for a progress bar. | `main_window.progress_signal.connect(my_progress_bar.setValue)` |
| `main_window.log_signal` | `pyqtSignal(str)` – thread‑safe logging. | `main_window.log_signal.connect(chat_window.append)` |

#### Useful tips

* **Never run long‑running code directly in a UI slot** – use `QThread` / `threading.Thread` and emit results via signals (`main_window.log_signal.emit(...)`).  
* If your plugin changes the theme or style, call `QApplication.instance().setPalette(...)`.  
* Access settings through `main_window.settings`.  
* **Never use global variables** inside a plugin – keep everything local or store state in `main_window.<your_attr>`.  
* Always log via `main_window.log_message()` instead of `print()`.  
* Check that a device is connected before issuing ADB commands (`main_window.check_device_connected()`).  
* Add `# -- coding: utf-8 --` at the top of every plugin file that contains non‑ASCII strings.  

If you have questions, open an **Issue** in the plugin repository or write to the project’s support chat (if it ever exists).

---

## 📦 Full guide to creating plugins for **xHelper α‑1.0.1 LTS/ATS**

Plugins are simple Python modules that are automatically loaded when the program starts. Each module must be placed in the `plugins/` folder (same level as `main.py`) and must export a single entry‑point function:

```python
def register(main_window):
    """Register the plugin in the main window."""
    ...
```

### Project structure

```
xHelper/
├─ main.py               # main code (do not modify)
└─ plugins/              # ← directory for all plugins
   ├─ example_plugin.py
   ├─ hardware_key_emulator.py
   └─ … (other plugins)
```

If the `plugins` folder does not exist – create it. Every file in this folder that defines a `register` function will be loaded by `XHelperMainWindow.load_plugins()` (the call is performed in the main‑window’s `__init__`).

### ⚙️ How plugin loading works

```python
def load_plugins(self):
    """Load all plugins from the plugins directory."""
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plugins_dir):
        self.log_message("Plugins folder not found – plugins not loaded.")
        return

    for fn in os.listdir(plugins_dir):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(plugins_dir, fn)
        spec = importlib.util.spec_from_file_location(f"plugin_{fn[:-3]}", path)
        if spec and spec.loader:
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    mod.register(self)  # ← main entry point
                    self.log_message(f"Plugin loaded: {fn}")
            except Exception as e:
                self.log_message(f"Error loading {fn}: {e}")
```

**What happens**

1. All `*.py` files in `plugins/` are enumerated.  
2. Each file is imported as a separate module (to avoid name clashes).  
3. If the module defines a `register` attribute, `mod.register(self)` is called.  
4. Any exception is caught and printed to the console log, but the loading of the remaining plugins continues.

### 🖼️ What you can add from `register(main_window)`

| Attribute / Method | Type | What it does | Example |
|--------------------|------|--------------|---------|
| `main_window.tabs` | `QTabWidget` | Main tab widget – add new tabs here. | `main_window.tabs.addTab(my_widget, "My Tab")` |
| `main_window.addDockWidget(area, widget)` | method | Add a `QDockWidget` (left/right/top/bottom). | `main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)` |
| `main_window.statusBar()` | `QStatusBar` | Status‑bar line. | `main_window.statusBar().showMessage("Plugin ready")` |
| `main_window.log_message(text)` | method | Write to the right‑hand console log. | `main_window.log_message("[MyPlugin] Started")` |
| `main_window.run_adb_command(command, device_specific=True)` | method | Execute any ADB command (optionally per‑device). | `main_window.run_adb_command("shell getprop ro.build.version.release")` |
| `main_window.settings` | `dict` | User‑defined settings (e.g. `adb_path`, `theme_dark`). | `if main_window.settings.get("theme_dark"): …` |
| `main_window.progress_signal` / `main_window.log_signal` | `pyqtSignal` | Signals that can be connected to UI elements. | `main_window.progress_signal.connect(my_progress_bar.setValue)` |
| `main_window.check_device_connected()` | method | Returns `True` if at least one device is connected. | `if not main_window.check_device_connected(): …` |
| `main_window.device_list` | `QListWidget` | List of connected devices (useful to get the selected serial). | `selected = main_window.device_list.currentItem().text()` |

If new attributes appear in future versions, plugins will simply ignore the unknown ones.

---

## 📐 Minimal “Hello‑World” plugin

```python
# -- coding: utf-8 --
def register(main_window):
    """The simplest plugin – adds a tab with a label."""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Hello, I am a simple example plugin!"))
    main_window.tabs.addTab(widget, "Example")
```

Save this file as `plugins/example_plugin.py` and restart **xHelper**. A new tab named **Example** with the text *Hello, I am a simple example plugin!* will appear on the top bar.

---

## 🛠️ 5️⃣ Creating a “full‑featured” plugin (Wi‑Fi manager)

Below is a step‑by‑step walkthrough for a typical use‑case.

### 5.1 Define the goal
**Example:** *Wi‑Fi control panel (enable/disable + show current SSID).*

### 5.2 Prepare UI elements

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QLineEdit
)
```

### 5.3 Create a thin ADB wrapper

```python
def _run_adb(main_window, cmd):
    """Simplified adb call that returns stdout (or empty string on error)."""
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(), text=True, timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Error: {e}")
        return ""
```

### 5.4 Action functions

```python
def get_status(main_window, lbl_status, lbl_ssid):
    out = _run_adb(main_window, "shell svc wifi")
    enabled = "enabled" in out.lower()
    lbl_status.setText(f"Status: {'Enabled' if enabled else 'Disabled'}")

    # Get current SSID
    dump = _run_adb(main_window, "shell dumpsys wifi")
    ssid = "—"
    for line in dump.splitlines():
        if "SSID:" in line or "SSID =" in line:
            ssid = line.split(":")[-1].strip().strip('"')
            break
    lbl_ssid.setText(f"SSID: {ssid}")

    # Update toggle‑button text
    btn.toggle.setText("Disable Wi‑Fi" if enabled else "Enable Wi‑Fi")
```

### 5.5 Assemble the UI in `register`

```python
def register(main_window):
    tab = QWidget()
    vbox = QVBoxLayout(tab)

    lbl_status = QLabel("Status: unknown")
    lbl_ssid   = QLabel("SSID: —")
    vbox.addWidget(lbl_status)
    vbox.addWidget(lbl_ssid)

    btn = QPushButton("Refresh")
    vbox.addWidget(btn)

    # Store the button so we can change its text later
    btn.toggle = btn

    # Connect actions
    btn.clicked.connect(lambda: get_status(main_window, lbl_status, lbl_ssid))
    # Request status immediately when the tab is opened
    get_status(main_window, lbl_status, lbl_ssid)

    main_window.tabs.addTab(tab, "Wi‑Fi Manager")
```

### 5.6 Result
After restarting **xHelper**, a new tab **Wi‑Fi Manager** appears. It shows the current Wi‑Fi state, the SSID, and a **Refresh** button. The button toggles Wi‑Fi on/off, and any errors are printed to the main log.

---

## 📦 6️⃣ Recommendations & best practices

| Why it matters | Recommendation |
|----------------|----------------|
| **Never block the UI** | Run long ADB calls in a separate thread (`QThread`/`QRunnable`). Use `main_window.log_signal.emit(...)` or `main_window.progress_signal.emit(...)` to update the UI safely. |
| **Avoid `show()` / `exec_()` in plugins** (except for `QMessageBox`) – the main window is already running; additional modal loops can freeze the interface. |
| **Keep UI changes in the main thread** – only modify widgets inside `register` or through signals. |
| **No global state** – everything should be local to the plugin or stored on `main_window`. |
| **Log through `main_window.log_message()`** – logs appear in the right‑hand console, visible to the user. |
| **Check for method / attribute existence** (`hasattr(main_window, "run_adb_command")`) before using them – the API may evolve. |
| **Never perform heavy operations on the UI thread** – use a worker thread and emit progress. |
| **Unique naming** – prefix your variables/functions (e.g., `myplugin_…`) to avoid clashes with other plugins. |
| **Validate device connection** (`main_window.check_device_connected()`) before sending ADB commands; give a friendly message if nothing is connected. |
| **Keep source files UTF‑8** (`# -- coding: utf-8 --`) so Russian text (if any) is handled correctly. |
| **Test plugins in isolation** – create a tiny script that launches `XHelperMainWindow` and loads only your plugin; this speeds up debugging. |

---

## 📚 7️⃣ List of “accepted” `main_window` attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tabs` | `QTabWidget` | Main tab widget – new tabs are added here. |
| `addDockWidget(area, widget)` | method | Add a `QDockWidget` to the specified area. |
| `statusBar()` | `QStatusBar` | The status‑bar line. |
| `log_message(text)` | method | Write a line to the right‑hand console widget. |
| `run_adb_command(command, device_specific=True)` | method | Execute an ADB command (optionally per‑device). |
| `settings` | `dict` | User settings (e.g., `adb_path`, `theme_dark`). |
| `progress_signal` / `log_signal` | `pyqtSignal` | Signals you can connect to UI elements (progress bar, log view). |
| `check_device_connected()` | method | Returns `True` if at least one device is connected. |
| `device_list` | `QListWidget` | List of connected devices; useful to retrieve the selected serial. |

If future versions add new attributes, existing plugins will simply ignore the unknown ones.

---

## 📦 8️⃣ Full example (advanced plugin) – **advanced_wifi_manager.py**

```python
# -- coding: utf-8 --
"""advanced_wifi_manager – full Wi‑Fi manager.

Features:
• Connection indicator (red/green) in the status bar;
• Table of known SSIDs with a list of available networks;
• Automatic refresh every 5 seconds;
• Ability to connect to the selected network (requires root – uses `svc wifi enable && am startservice ...`)."""

import subprocess
import re
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QColor, QPalette
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

# ----------------------------------------------------------------------
# Helper function – run adb and return stdout
# ----------------------------------------------------------------------
def _adb(main_window, cmd):
    """Run adb command and return the output (or empty string on error)."""
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(), text=True, timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Error: {e}")
        return ""

# ----------------------------------------------------------------------
# Main registration function
# ----------------------------------------------------------------------
def register(main_window):
    tab = QWidget()
    layout = QVBoxLayout(tab)

    # ---------------------- status bar (colored indicator) ----------------------
    wifi_indicator = QLabel()
    wifi_indicator.setFixedSize(12, 12)
    wifi_indicator.setStyleSheet("border-radius:6px; background:#ff5555;")
    main_window.statusBar().addPermanentWidget(wifi_indicator)

    # ---------------------- top control bar ----------------------
    top_bar = QHBoxLayout()
    btn_refresh = QPushButton("Refresh")
    btn_toggle = QPushButton("Enable Wi‑Fi")
    lbl_status = QLabel("Status: —")
    top_bar.addWidget(btn_refresh)
    top_bar.addWidget(btn_toggle)
    top_bar.addWidget(lbl_status)
    top_bar.addStretch()
    top_bar.addWidget(QLabel("Current SSID:"))
    lbl_ssid = QLabel("—")
    top_bar.addWidget(lbl_ssid)
    layout.addLayout(top_bar)

    # ---------------------- table of available networks ----------------------
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["SSID", "Signal (dBm)"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    # ---------------------- "Connect" button ----------------------
    btn_connect = QPushButton("Connect to selected network")
    btn_connect.setEnabled(False)
    layout.addWidget(btn_connect)

    # ------------------------------------------------------------------
    # Internal helper functions
    # ------------------------------------------------------------------
    def update_status():
        # Is Wi‑Fi enabled?
        out = _adb(main_window, "shell svc wifi")
        enabled = "enabled" in out.lower()
        wifi_indicator.setStyleSheet(
            f"border-radius:6px; background:{'#55ff55' if enabled else '#ff5555'};")
        btn_toggle.setText("Disable Wi‑Fi" if enabled else "Enable Wi‑Fi")
        lbl_status.setText(f"Status: {'Enabled' if enabled else 'Disabled'}")

        # Current SSID
        dump = _adb(main_window, "shell dumpsys wifi")
        ssid = "—"
        for line in dump.splitlines():
            if "SSID:" in line or "SSID =" in line:
                ssid = line.split(":")[-1].strip().strip('"')
                break
        lbl_ssid.setText(ssid)

    def scan_networks():
        """Get a list of available Wi‑Fi networks (requires ACCESS_WIFI_STATE permission)."""
        out = _adb(main_window, "shell dumpsys wifi")
        # Look for lines like: "SSID: MyNetwork, BSSID: xx:xx..., RSSI: -63"
        networks = []
        for line in out.splitlines():
            if "SSID:" in line and "RSSI:" in line:
                ssid_match = re.search(r"SSID:\s*([^\s,]+)", line)
                rssi_match = re.search(r"RSSI:\s*(-?\d+)", line)
                if ssid_match and rssi_match:
                    networks.append((ssid_match.group(1), int(rssi_match.group(1))))
        # Update table
        table.setRowCount(len(networks))
        for row, (ssid, rssi) in enumerate(networks):
            table.setItem(row, 0, QTableWidgetItem(ssid))
            table.setItem(row, 1, QTableWidgetItem(str(rssi)))
        btn_connect.setEnabled(bool(networks))

    def toggle_wifi():
        out = _adb(main_window, "shell svc wifi")
        if "enabled" in out.lower():
            _adb(main_window, "shell svc wifi disable")
        else:
            _adb(main_window, "shell svc wifi enable")
        update_status()

    def connect_to_selected():
        cur = table.currentItem()
        if not cur:
            QMessageBox.warning(tab, "Warning", "Select a network in the table")
            return
        ssid = table.item(cur.row(), 0).text()
        # Command to connect (requires root or a saved profile)
        # Simplified version uses `am startservice` (can be improved):
        _adb(main_window,
             f'shell am startservice -n com.android.settings/.wifi.WifiSettings '
             f'--es ssid "{ssid}"')
        QMessageBox.information(tab, "Connection",
                                f"Attempting to connect to {ssid}. "
                                "If a password is required, open Wi‑Fi settings manually.")

    # ------------------------------------------------------------------
    # Connect signals/slots
    # ------------------------------------------------------------------
    btn_refresh.clicked.connect(lambda: (update_status(), scan_networks()))
    btn_toggle.clicked.connect(toggle_wifi)
    btn_connect.clicked.connect(connect_to_selected)

    # Automatic timer (5 seconds) – refresh status and scan
    timer = QTimer(main_window)
    timer.setInterval(5000)
    timer.timeout.connect(lambda: (update_status(), scan_networks()))
    timer.start()
    # Initial data fetch
    update_status()
    scan_networks()

    # --------------------------------------------------------------
    # Add the tab to the main window
    # --------------------------------------------------------------
    main_window.tabs.addTab(tab, "Wi‑Fi Manager")
```

**What this demonstrates**

- Use of `QTimer` for periodic updates.  
- Dynamic colour change of a `QLabel` used as a status‑indicator.  
- A `QTableWidget` for listing SSIDs and signal strengths.  
- Interaction with `main_window.log_message`.  
- Multiple calls to the custom `_adb` wrapper.  

---

## 🧩 9️⃣ Debugging & testing plugins

### 1️⃣ Run a stand‑alone test

```bash
python - <<'PY'
import sys
from PyQt6.QtWidgets import QApplication
from main import XHelperMainWindow

app = QApplication(sys.argv)
win = XHelperMainWindow()
win.show()
sys.exit(app.exec())
PY
```

After the window appears, you can drop your plugin into the `plugins/` directory and see the effect instantly.

### 2️⃣ Check the log
`print()` statements do **not** appear in the UI. Use `main_window.log_message("…")`. The messages show up in the right‑hand console and, if the *log‑to‑file* option is enabled, also in a file.

### 3️⃣ Track errors
If a plugin fails to load, the console log will contain something like:

```
[ERROR] Error loading my_plugin.py: Traceback (most recent call last):
...
```

Fix the traceback and restart the program.

### 4️⃣ Verify name conflicts
Make sure your plugin does **not** define global variables that clash with other plugins (e.g., `btn`, `timer`). Prefix your names (e.g., `myplugin_btn`) if needed.

### 5️⃣ Test with multiple devices
If the *Run on all selected devices* checkbox is enabled in xHelper, your plugin will automatically execute on every checked device (handled by the `device_specific=True` argument of `run_adb_command`). To limit execution to a single device, omit that flag.

---

## 📐 10️⃣ Quick recap of plugin‑creation steps

| Step | Action |
|------|--------|
| **1️⃣** | Create the file `plugins/<your_plugin>.py`. |
| **2️⃣** | Add `# -- coding: utf-8 --` at the very top (required for non‑ASCII strings). |
| **3️⃣** | Implement `def register(main_window):` – this is the entry point. |
| **4️⃣** | Inside `register` create your UI (usually a `QWidget` with a layout). |
| **5️⃣** | Add the widget to the UI via `main_window.tabs.addTab(widget, "Title")` **or** `main_window.addDockWidget(...)`. |
| **6️⃣** | Use `main_window.run_adb_command(...)`, `main_window.log_message(...)`, `main_window.settings`, etc., as needed. |
| **7️⃣** | For long‑running tasks, spawn a `QThread`/`QRunnable` and emit `main_window.log_signal` / `main_window.progress_signal`. |
| **8️⃣** | Save the file and restart **xHelper**. |
| **9️⃣** | Look at the right‑hand console, fix any errors, and optionally add `QMessageBox` dialogs for critical problems. |

---

## 🎉 Some inspiration

- **Lag‑free UI:** Run heavy ADB queries in a separate thread and push results back via signals (as shown in the *WorkerThread* pattern).  
- **Custom settings:** If your plugin needs extra parameters (e.g., timeout), add them to `main_window.settings` through a small configuration dialog and persist them in `~/.xhelper_prealpha_config.json`.  
- **In‑code documentation:** Write docstrings for every function – they appear automatically in IDE tool‑tips.  
- **Localization:** If you intend to distribute the plugin, use `QTranslator` and `.qm` files (xHelper already has a localisation system you can plug into).  

---

## 📌 TL;DR

- **A plugin = a Python file with `register(main_window)` placed in `plugins/`.**  
- **`register` receives the fully‑initialised `XHelperMainWindow` object**, giving you access to tabs, dock widgets, ADB execution, logging, settings, and signals.  
- **Create UI elements, hook them up, call ADB when needed, log everything**, and **avoid blocking the UI**.  
- **When your file is saved, restart xHelper** and the new tab/button appears without touching the core code.  

You now have everything you need to extend **xHelper** with your own ideas – from advanced Wi‑Fi management to hardware‑key emulation, screencasting, automated tests, CI integration, and beyond. Happy hacking! 🚀
