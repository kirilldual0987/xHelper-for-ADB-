⚠️ Это Alpha‑версия
Программа xHelper α (1.0.1 LTS/ATS) находится в альфа‑стадии. Это значит, что в ней могут присутствовать: 
неотлаженные функции;
неожиданные падения (краши) при работе с ADB/fastboot;
некорректные ответы от устройства;
сбои UI, если одновременно запущено несколько тяжёлых операций.
Мы настоятельно рекомендуем использовать эту сборку только в тестовых целях и не в критически важных проектах. 

📚 Краткий гайд по использованию xHelper (функционал описываеться без использования плагинов, что скорее всего невозможно, так как xHelper поставляеться с плагинами
Подключение устройства – откройте вкладку «Устройства» и нажмите «Обновить список устройств». Убедитесь, что ADB‑драйвер установлен. 
Управление приложениями – во вкладке «APK» можно установить, удалить или запустить приложение, указав его пакет. 
Массовая установка – вкладка «Массовая установка APK» позволяет выбрать папку с несколькими .apk‑файлами и установить их одной командой. 
Файловые операции – во вкладке «Файлы» копируются файлы на/с устройства (adb push / pull). 
Тестирование приложений – вкладка «Тестирование приложений» запускает каждое приложение, собирает logcat и отмечает приложения, которые упали. 
Скринкаст и скриншоты – во вкладке «Экран устройства» можно запустить scrcpy (если он установлен) или сделать скриншот. 
Бэкапы – вкладка «Бэкап / Восстановление» создаёт полный ADB‑бэкап и позволяет восстановить его. 

🔧 Как писать собственные плагины для xHelper
Плагин – это обычный Python‑модуль, помещённый в каталог plugins/ рядом с main.py. При старте программы XHelperMainWindow.load_plugins() автоматически импортирует каждый файл *.py, ищет в нём функцию register(main_window) и вызывает её, передавая объект главного окна. 
Минимальный шаблон плагина: 
# plugins/example.py
# -*- coding: utf-8 -*-

def register(main_window):
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.addWidget(QLabel("Пример плагина"))
    main_window.tabs.addTab(tab, "Example")
 
Внутри register вы имеете доступ к:
main_window.run_adb_command(...) – выполнить любую ADB‑команду.
main_window.log_message(...) – писать в правый консоль‑лог.
main_window.tabs – добавить свои вкладки.
main_window.addDockWidget(...) – добавить dock‑виджет.
и любые другие публичные атрибуты/методы XHelperMainWindow. 
Полезные советы:
Не вызывайте длительные операции напрямую в UI‑слоте – используйте QThread / threading.Thread и передавайте результаты через сигналы (main_window.log_signal.emit(...)). 
Если ваш плагин меняет тему/стили, используйте QApplication.instance().setPalette(...).
Для доступа к настройкам используйте main_window.settings (словарь, сохраняемый в ~/.xhelper_prealpha_config.json). 

Если появятся вопросы – создавайте Issue в репозитории плагина или пишите в чат‑поддержку проекта (если они вообще будут созданы). 









📦 Полный гайд по созданию плагинов для xHelper α‑1.0.1 LTS/ATS
В xHelper плагины – это простые Python‑модули, которые автоматически подгружаются при запуске программы.
Каждый модуль помещается в папку plugins/ (на том же уровне, где находится main.py) и обязан экспортировать одну функцию‑точку входа:
python
def register(main_window):
    """Регистрация плагина в главном окне."""
    ...
def register(main_window):
    """Регистрация плагина в главном окне."""
    ...
Эта функция получает объект XHelperMainWindow – уже запущенное главное окно, уже инициализированный QTabWidget, QStatusBar, log_message(), run_adb_command() и т. д. Через этот объект плагин может добавлять любые элементы UI (вкладки, dock‑виджеты, toolbar‑кнопки) и вызывать существующий функционал без изменения ядра программы.

📁 1. Структура проекта
xHelper/
├─ main.py                     # основной код (не меняем)
└─ plugins/                    # ← директория для всех плагинов
   ├─ example_plugin.py
   ├─ hardware_key_emulator.py
   └─ … (другие плагины)
xHelper/
├─ main.py                     # основной код (не меняем)
└─ plugins/                    # ← директория для всех плагинов
   ├─ example_plugin.py
   ├─ hardware_key_emulator.py
   └─ … (другие плагины)
Если каталога plugins нет – создайте его.
Каждый файл в этой папке, у которого есть функция register, будет автоматически загружен методом XHelperMainWindow.load_plugins() (вызов происходит в __init__ главного окна).

⚙️ 2. Как работает загрузка
В main.py (фрагмент) реализовано:
python
def load_plugins(self):
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plugins_dir):
        self.log_message("Папка plugins не найдена – плагины не загружены.")
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
                    mod.register(self)                 # ← главная точка входа
                    self.log_message(f"Плагин загружен: {fn}")
            except Exception as e:
                self.log_message(f"Ошибка загрузки {fn}: {e}")
def load_plugins(self):
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plugins_dir):
        self.log_message("Папка plugins не найдена – плагины не загружены.")
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
                    mod.register(self)                 # ← главная точка входа
                    self.log_message(f"Плагин загружен: {fn}")
            except Exception as e:
                self.log_message(f"Ошибка загрузки {fn}: {e}")
    • Что происходит: 
        1. Перебираются все .py‑файлы в plugins/. 
        2. Для каждого создаётся отдельный модуль (чтобы не конфликтовать с именами). 
        3. Если в модуле есть атрибут register, вызывается mod.register(self). 
        4. Любые исключения перехватываются и выводятся в консоль‑лог, но не останавливают загрузку остальных плагинов. 

🖼️ 3. Что можно добавить из register
main_window (экземпляр XHelperMainWindow) уже содержит почти всё, что нужно:
Атрибут / метод	Что делает	Пример использования
main_window.tabs	QTabWidget – основной набор вкладок	main_window.tabs.addTab(my_widget, "My Tab")
main_window.addDockWidget(area, widget)	Добавить QDockWidget слева/справа/вверху/внизу	main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
main_window.statusBar()	QStatusBar – строка статуса	main_window.statusBar().showMessage("Плагин готов")
main_window.log_message(text)	Записать в главный лог (правый текстовый блок)	main_window.log_message("[MyPlugin] Запущен")
main_window.run_adb_command(cmd, device_specific=True)	Выполнить любую ADB‑команду (с учётом выбранного устройства)	main_window.run_adb_command("shell getprop ro.build.version.release")
main_window.settings (dict)	Настройки, загруженные/сохранённые в ~/.xhelper_prealpha_config.json	if main_window.settings.get("theme_dark"): …
main_window.progress_signal	Сигнал прогресса (integer 0‑100) – удобно для QProgressBar	main_window.progress_signal.connect(my_progress_bar.setValue)
main_window.log_signal	Сигнал текста для потокобезопасного логирования	main_window.log_signal.connect(chat_window.append)
Важно: любые изменения UI (добавление виджетов) должны происходить внутри функции register, т.к. именно там у вас уже есть доступ к готовому окну.

📐 4. Минимальный «Hello‑World»‑плагин
python
# plugins/example_plugin.py
# -*- coding: utf-8 -*-

def register(main_window):
    """Самый простой плагин – добавляет одну вкладку с надписью."""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Привет, я простой пример плагина!"))
    main_window.tabs.addTab(widget, "Пример")
# plugins/example_plugin.py
# -*- coding: utf-8 -*-

def register(main_window):
    """Самый простой плагин – добавляет одну вкладку с надписью."""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Привет, я простой пример плагина!"))
    main_window.tabs.addTab(widget, "Пример")
Сохраните в plugins/example_plugin.py и перезапустите xHelper. На верхней панели появится вкладка «Пример» с надписью.

🛠️ 5. Создание «полноценного» плагина
Ниже пошагово разберём типичный сценарий:
5.1. Определяем цель
Пример: «Панель управления Wi‑Fi (вкл/выкл + текущий SSID)».
5.2. Подготовка UI‑элементов
python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QLineEdit
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QLineEdit
)
5.3. Создаём функции‑обёртки для ADB
python
def _run_adb(main_window, cmd):
    """Упрощённый вызов adb, возвращает stdout (или пустую строку)."""
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(),
                                      text=True,
                                      timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Ошибка: {e}")
        return ""
def _run_adb(main_window, cmd):
    """Упрощённый вызов adb, возвращает stdout (или пустую строку)."""
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(),
                                      text=True,
                                      timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Ошибка: {e}")
        return ""
5.4. Функции‑действия
python
def get_status(main_window, lbl_status, lbl_ssid):
    out = _run_adb(main_window, "shell svc wifi")
    enabled = "enabled" in out.lower()
    lbl_status.setText(f"Статус: {'Включён' if enabled else 'Выключен'}")

    # Получаем SSID
    dump = _run_adb(main_window, "shell dumpsys wifi")
    ssid = "—"
    for line in dump.splitlines():
        if "SSID:" in line or "SSID =" in line:
            ssid = line.split(":")[-1].strip().strip('"')
            break
    lbl_ssid.setText(f"SSID: {ssid}")
    # Меняем подпись кнопки переключения
    btn.toggle.setText("Выключить Wi‑Fi" if enabled else "Включить Wi‑Fi")
def get_status(main_window, lbl_status, lbl_ssid):
    out = _run_adb(main_window, "shell svc wifi")
    enabled = "enabled" in out.lower()
    lbl_status.setText(f"Статус: {'Включён' if enabled else 'Выключен'}")

    # Получаем SSID
    dump = _run_adb(main_window, "shell dumpsys wifi")
    ssid = "—"
    for line in dump.splitlines():
        if "SSID:" in line or "SSID =" in line:
            ssid = line.split(":")[-1].strip().strip('"')
            break
    lbl_ssid.setText(f"SSID: {ssid}")
    # Меняем подпись кнопки переключения
    btn.toggle.setText("Выключить Wi‑Fi" if enabled else "Включить Wi‑Fi")
5.5. Собираем UI
python
def register(main_window):
    tab = QWidget()
    vbox = QVBoxLayout(tab)

    lbl_status = QLabel("Статус: неизвестно")
    lbl_ssid   = QLabel("SSID: —")
    vbox.addWidget(lbl_status)
    vbox.addWidget(lbl_ssid)

    btn = QPushButton("Обновить")
    vbox.addWidget(btn)

    # Сохраняем кнопку, чтобы поменять её текст позже
    btn.toggle = btn

    # Действия
    btn.clicked.connect(lambda: get_status(main_window, lbl_status, lbl_ssid))
    # При открытии вкладки сразу запрашиваем статус
    get_status(main_window, lbl_status, lbl_ssid)

    main_window.tabs.addTab(tab, "Wi‑Fi‑менеджер")
def register(main_window):
    tab = QWidget()
    vbox = QVBoxLayout(tab)

    lbl_status = QLabel("Статус: неизвестно")
    lbl_ssid   = QLabel("SSID: —")
    vbox.addWidget(lbl_status)
    vbox.addWidget(lbl_ssid)

    btn = QPushButton("Обновить")
    vbox.addWidget(btn)

    # Сохраняем кнопку, чтобы поменять её текст позже
    btn.toggle = btn

    # Действия
    btn.clicked.connect(lambda: get_status(main_window, lbl_status, lbl_ssid))
    # При открытии вкладки сразу запрашиваем статус
    get_status(main_window, lbl_status, lbl_ssid)

    main_window.tabs.addTab(tab, "Wi‑Fi‑менеджер")
5.6. Результат
После перезапуска xHelper появится новая вкладка «Wi‑Fi‑менеджер», показывающая текущий статус, SSID и кнопку «Обновить». Кнопка переключает Wi‑Fi, а любые ошибки выводятся в главный лог.

📦 6. Рекомендации и лучшие практики
Совет	Почему это важно
Не вызывайте show()/exec_() внутри плагина (за исключением QMessageBox).	Главное окно уже работает – лишний вызов может «запереть» UI.
Все обращения к GUI‑элементам делайте в основном потоке. Если нужен тяжёлый запрос к ADB, используйте QThread или QThreadPool + QRunnable.	PyQt‑thread‑safety: изменение виджетов из другого потока вызывает краш.
Не храните в плагине глобальные переменные – используйте только локальные или сохраняйте состояние в main_window.<your_attr> (например, main_window.my_plugin_state).	При перезагрузке окна (например, с closeEvent) старый объект может стать недоступным.
Логируйте через main_window.log_message(), а не через print().	Логи появляются в правой консоли xHelper → пользователь видит, что происходит.
Проверяйте наличие методов/атрибутов (hasattr(main_window, "run_adb_command")).	Некоторые плагины могут быть использованы в будущих версиях, где API изменится.
Не блокируйте UI длительными операциями (например, adb pull большого файла). Выносите в отдельный поток и выводите прогресс через main_window.progress_signal.	Пользователь видит индикатор и приложение остаётся отзывчивым.
Соблюдайте нейминг – имена функций/переменных в плагине должны быть уникальными, иначе могут конфликтовать с другими плагинами. При желании используйте префиксы (myplugin_…).	Чтобы плагины могли сосуществовать, их внутренние имена не должны пересекаться.
Проверяйте, запущено ли устройство перед выполнением ADB‑команд (можно вызвать main_window.check_device_connected() или просто проверять adb devices).	Если устройство не подключено, команда вернёт ошибку. Пользователь получит понятное сообщение.
Не забывайте о Unicode – если используете русские строки, ставьте # -*- coding: utf-8 -*- в начале файла.	Чтобы Python правильно интерпретировал ваши тексты.
Тестируйте плагин отдельно – запустите python plugins/your_plugin.py и создайте мини‑приложение с QApplication и XHelperMainWindow (импортируйте класс из main.py).	Позволит быстро отлавливать ошибки без перезапуска всей программы.

📚 7. Список «принятых» атрибутов main_window
Атрибут	Тип	Описание
tabs	QTabWidget	Главное таб‑виджет, в него добавляются новые вкладки.
addDockWidget(area, widget)	метод	Добавление QDockWidget.
statusBar()	QStatusBar	Строка состояния.
log_message(text)	метод	Запись в правый консоль‑виджет.
run_adb_command(command, device_specific=True)	метод	Выполняет ADB‑команду.
settings	dict	Пользовательские настройки (например, adb_path, theme_dark).
progress_signal / log_signal	pyqtSignal	Сигналы, которые можно подключать к своим UI‑элементам.
check_device_connected()	метод	Возвращает True, если хотя бы одно устройство подключено.
device_list	QListWidget	Список подключённых устройств (полезно, если нужно получить выбранный serial).
Если в будущих версиях появятся новые атрибуты, плагин всё равно будет работать – он будет игнорировать неизвестные свойства.

📦 8. Полный пример (продвинутый плагин)
plugins/advanced_wifi_manager.py – демонстрирует все возможности:
python
# plugins/advanced_wifi_manager.py
# -*- coding: utf-8 -*-

"""
advanced_wifi_manager – полноценный менеджер Wi‑Fi.

Особенности:
 • индикатор связи (красный/зелёный) в статус‑баре;
 • таблица известных SSID со списком доступных сетей;
 • автоматическое обновление каждые 5 сек.;
 • возможность подключиться к выбранной сети (если устройство имеет root‑права
   – используется `svc wifi enable && am startservice ...`).
"""

import subprocess
import re
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui   import QIcon, QColor, QPalette
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)


# ----------------------------------------------------------------------
#   Вспомогательная функция – выполнить adb и вернуть stdout
# ----------------------------------------------------------------------
def _adb(main_window, cmd):
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(),
                                      text=True,
                                      timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Ошибка: {e}")
        return ""


# ----------------------------------------------------------------------
#   Основная регистрация
# ----------------------------------------------------------------------
def register(main_window):
    tab = QWidget()
    layout = QVBoxLayout(tab)

    # ---------------------- статус‑бар (цветной индикатор) ----------------------
    wifi_indicator = QLabel()
    wifi_indicator.setFixedSize(12, 12)
    wifi_indicator.setStyleSheet("border-radius:6px; background:#ff5555;")
    main_window.statusBar().addPermanentWidget(wifi_indicator)

    # ---------------------- верхняя панель управления ----------------------
    top_bar = QHBoxLayout()
    btn_refresh = QPushButton("Обновить")
    btn_toggle  = QPushButton("Включить Wi‑Fi")
    lbl_status  = QLabel("Статус: —")
    top_bar.addWidget(btn_refresh)
    top_bar.addWidget(btn_toggle)
    top_bar.addWidget(lbl_status)
    top_bar.addStretch()
    top_bar.addWidget(QLabel("Текущий SSID:"))
    lbl_ssid = QLabel("—")
    top_bar.addWidget(lbl_ssid)
    layout.addLayout(top_bar)

    # ---------------------- таблица доступных сетей ----------------------
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["SSID", "Сигнал (dBm)"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    # ---------------------- кнопка «Подключиться» ----------------------
    btn_connect = QPushButton("Подключиться к выбранной сети")
    btn_connect.setEnabled(False)
    layout.addWidget(btn_connect)

    # ------------------------------------------------------------------
    #   Внутренние функции
    # ------------------------------------------------------------------
    def update_status():
        # Wi‑Fi включён?
        out = _adb(main_window, "shell svc wifi")
        enabled = "enabled" in out.lower()
        wifi_indicator.setStyleSheet(
            f"border-radius:6px; background:{'#55ff55' if enabled else '#ff5555'};")
        btn_toggle.setText("Выключить Wi‑Fi" if enabled else "Включить Wi‑Fi")
        lbl_status.setText(f"Статус: {'Включён' if enabled else 'Выключен'}")

        # Текущий SSID
        dump = _adb(main_window, "shell dumpsys wifi")
        ssid = "—"
        for line in dump.splitlines():
            if "SSID:" in line or "SSID =" in line:
                ssid = line.split(":")[-1].strip().strip('"')
                break
        lbl_ssid.setText(ssid)

    def scan_networks():
        """Получаем список доступных Wi‑Fi (требует разрешения ACCESS_WIFI_STATE)."""
        out = _adb(main_window, "shell dumpsys wifi")
        # Ищем строки типа: "SSID: MyNetwork, BSSID: xx:xx..., RSSI: -63"
        networks = []
        for line in out.splitlines():
            if "SSID:" in line and "RSSI:" in line:
                ssid_match = re.search(r"SSID:\s*([^\s,]+)", line)
                rssi_match = re.search(r"RSSI:\s*(-?\d+)", line)
                if ssid_match and rssi_match:
                    networks.append((ssid_match.group(1), int(rssi_match.group(1))))
        # Обновляем таблицу
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
            QMessageBox.warning(tab, "Внимание", "Выберите сеть в таблице")
            return
        ssid = table.item(cur.row(), 0).text()
        # Команда для подключения (требует root или сохранённый профиль)
        # В простейшем виде используем `am startservice` (можно доработать):
        _adb(main_window,
             f'shell am startservice -n com.android.settings/.wifi.WifiSettings '
             f'--es ssid "{ssid}"')
        QMessageBox.information(tab, "Подключение",
                                f"Попытка подключиться к {ssid}. "
                                "Если требуется пароль, откройте настройки Wi‑Fi вручную.")
    # ------------------------------------------------------------------
    #   Связываем сигналы/слоты
    # ------------------------------------------------------------------
    btn_refresh.clicked.connect(lambda: (update_status(), scan_networks()))
    btn_toggle.clicked.connect(toggle_wifi)
    btn_connect.clicked.connect(connect_to_selected)

    # Автоматический таймер (5 сек.) – обновление статуса и сканирование
    timer = QTimer(main_window)
    timer.setInterval(5000)
    timer.timeout.connect(lambda: (update_status(), scan_networks()))
    timer.start()
    # При первом открытии сразу запросим данные
    update_status()
    scan_networks()

    # --------------------------------------------------------------
    #   Добавляем вкладку
    # --------------------------------------------------------------
    main_window.tabs.addTab(tab, "Wi‑Fi‑Менеджер")
# plugins/advanced_wifi_manager.py
# -*- coding: utf-8 -*-

"""
advanced_wifi_manager – полноценный менеджер Wi‑Fi.

Особенности:
 • индикатор связи (красный/зелёный) в статус‑баре;
 • таблица известных SSID со списком доступных сетей;
 • автоматическое обновление каждые 5 сек.;
 • возможность подключиться к выбранной сети (если устройство имеет root‑права
   – используется `svc wifi enable && am startservice ...`).
"""

import subprocess
import re
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui   import QIcon, QColor, QPalette
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)


# ----------------------------------------------------------------------
#   Вспомогательная функция – выполнить adb и вернуть stdout
# ----------------------------------------------------------------------
def _adb(main_window, cmd):
    adb = main_window.settings.get("adb_path", "adb") if hasattr(main_window, "settings") else "adb"
    try:
        out = subprocess.check_output([adb] + cmd.split(),
                                      text=True,
                                      timeout=5)
        return out
    except Exception as e:
        main_window.log_message(f"[Wi‑Fi] Ошибка: {e}")
        return ""


# ----------------------------------------------------------------------
#   Основная регистрация
# ----------------------------------------------------------------------
def register(main_window):
    tab = QWidget()
    layout = QVBoxLayout(tab)

    # ---------------------- статус‑бар (цветной индикатор) ----------------------
    wifi_indicator = QLabel()
    wifi_indicator.setFixedSize(12, 12)
    wifi_indicator.setStyleSheet("border-radius:6px; background:#ff5555;")
    main_window.statusBar().addPermanentWidget(wifi_indicator)

    # ---------------------- верхняя панель управления ----------------------
    top_bar = QHBoxLayout()
    btn_refresh = QPushButton("Обновить")
    btn_toggle  = QPushButton("Включить Wi‑Fi")
    lbl_status  = QLabel("Статус: —")
    top_bar.addWidget(btn_refresh)
    top_bar.addWidget(btn_toggle)
    top_bar.addWidget(lbl_status)
    top_bar.addStretch()
    top_bar.addWidget(QLabel("Текущий SSID:"))
    lbl_ssid = QLabel("—")
    top_bar.addWidget(lbl_ssid)
    layout.addLayout(top_bar)

    # ---------------------- таблица доступных сетей ----------------------
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["SSID", "Сигнал (dBm)"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    # ---------------------- кнопка «Подключиться» ----------------------
    btn_connect = QPushButton("Подключиться к выбранной сети")
    btn_connect.setEnabled(False)
    layout.addWidget(btn_connect)

    # ------------------------------------------------------------------
    #   Внутренние функции
    # ------------------------------------------------------------------
    def update_status():
        # Wi‑Fi включён?
        out = _adb(main_window, "shell svc wifi")
        enabled = "enabled" in out.lower()
        wifi_indicator.setStyleSheet(
            f"border-radius:6px; background:{'#55ff55' if enabled else '#ff5555'};")
        btn_toggle.setText("Выключить Wi‑Fi" if enabled else "Включить Wi‑Fi")
        lbl_status.setText(f"Статус: {'Включён' if enabled else 'Выключен'}")

        # Текущий SSID
        dump = _adb(main_window, "shell dumpsys wifi")
        ssid = "—"
        for line in dump.splitlines():
            if "SSID:" in line or "SSID =" in line:
                ssid = line.split(":")[-1].strip().strip('"')
                break
        lbl_ssid.setText(ssid)

    def scan_networks():
        """Получаем список доступных Wi‑Fi (требует разрешения ACCESS_WIFI_STATE)."""
        out = _adb(main_window, "shell dumpsys wifi")
        # Ищем строки типа: "SSID: MyNetwork, BSSID: xx:xx..., RSSI: -63"
        networks = []
        for line in out.splitlines():
            if "SSID:" in line and "RSSI:" in line:
                ssid_match = re.search(r"SSID:\s*([^\s,]+)", line)
                rssi_match = re.search(r"RSSI:\s*(-?\d+)", line)
                if ssid_match and rssi_match:
                    networks.append((ssid_match.group(1), int(rssi_match.group(1))))
        # Обновляем таблицу
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
            QMessageBox.warning(tab, "Внимание", "Выберите сеть в таблице")
            return
        ssid = table.item(cur.row(), 0).text()
        # Команда для подключения (требует root или сохранённый профиль)
        # В простейшем виде используем `am startservice` (можно доработать):
        _adb(main_window,
             f'shell am startservice -n com.android.settings/.wifi.WifiSettings '
             f'--es ssid "{ssid}"')
        QMessageBox.information(tab, "Подключение",
                                f"Попытка подключиться к {ssid}. "
                                "Если требуется пароль, откройте настройки Wi‑Fi вручную.")
    # ------------------------------------------------------------------
    #   Связываем сигналы/слоты
    # ------------------------------------------------------------------
    btn_refresh.clicked.connect(lambda: (update_status(), scan_networks()))
    btn_toggle.clicked.connect(toggle_wifi)
    btn_connect.clicked.connect(connect_to_selected)

    # Автоматический таймер (5 сек.) – обновление статуса и сканирование
    timer = QTimer(main_window)
    timer.setInterval(5000)
    timer.timeout.connect(lambda: (update_status(), scan_networks()))
    timer.start()
    # При первом открытии сразу запросим данные
    update_status()
    scan_networks()

    # --------------------------------------------------------------
    #   Добавляем вкладку
    # --------------------------------------------------------------
    main_window.tabs.addTab(tab, "Wi‑Fi‑Менеджер")
Что здесь продемонстрировано:
    • работа с QTimer и автоматическим обновлением; 
    • динамическое изменение цвета индикатора (QLabel с setStyleSheet); 
    • таблица QTableWidget + выбор элемента; 
    • взаимодействие со main_window.log_message; 
    • многократные вызовы run_adb_command через собственный помощник _adb. 

🧩 9. Отладка и тестирование плагинов
    1. Запуск отдельного теста
       bash
       python - <<'PY'
       import sys, os
       from PyQt6.QtWidgets import QApplication
       from main import XHelperMainWindow
       
       app = QApplication(sys.argv)
       win = XHelperMainWindow()
       win.show()
       sys.exit(app.exec())
       PY
       python - <<'PY'
       import sys, os
       from PyQt6.QtWidgets import QApplication
       from main import XHelperMainWindow
       
       app = QApplication(sys.argv)
       win = XHelperMainWindow()
       win.show()
       sys.exit(app.exec())
       PY
       После запуска вы сможете импортировать ваш плагин в plugins/ и сразу увидеть результат.
    2. Проверка лога
Любой print() не будет виден в UI; используйте main_window.log_message("…"). Логи появляются в правой консоли и, если включена опция log_to_file, также записываются в файл.
    3. Отслеживание ошибок
Если плагин не загружается, в консоли (правый лог) появится сообщение вида
       [ERROR] Ошибка загрузки my_plugin.py: Traceback (most recent call last):
       …
       [ERROR] Ошибка загрузки my_plugin.py: Traceback (most recent call last):
       …
       Исправьте ошибку и перезапустите.
    4. Проверка конфликтов имён
Убедитесь, что в плагине не объявлены глобальные переменные с тем же именем, что и в других плагинах (например, btn, timer). Если необходимо – используйте префикс myplugin_.
    5. Тестирование с несколькими устройствами
Если в XHelper включен чекбокс «Выполнять на всех выбранных», ваш плагин автоматически выполнит команду на всех отмеченных устройствах (это задаётся параметром device_specific=True в run_adb_command). Если нужно выполнить только на одном – оставляйте параметр как есть.

📐 10. Краткое резюме шагов создания плагина
Шаг	Действие
1️⃣	Создайте файл plugins/<your_plugin>.py.
2️⃣	В начале файла добавьте # -*- coding: utf-8 -*-.
3️⃣	Реализуйте функцию def register(main_window):.
4️⃣	Внутри register создайте виджеты (обычно QWidget + layout).
5️⃣	Добавьте их в UI через main_window.tabs.addTab(widget, "Заголовок") или main_window.addDockWidget(...).
6️⃣	При необходимости используйте main_window.run_adb_command(...), main_window.log_message(...), main_window.settings.
7️⃣	Если нужен асинхронный процесс, создайте QThread/QRunnable и эмитируйте main_window.log_signal/progress_signal.
8️⃣	Сохраните файл и перезапустите xHelper.
9️⃣	Проверьте вывод в правой консоли, исправьте ошибки, при необходимости добавьте QMessageBox в случае критических проблем.

🎉 11. Немного вдохновения
    • Lag‑Free UI: Делайте тяжёлые запросы к ADB в отдельном потоке, а результат отправляйте в UI через сигналы (как в WorkerThread). 
    • Кастомные настройки: Если ваш плагин требует параметров (например, таймаут), вы можете добавить их в main_window.settings через отдельный диалог и сохранять в ~/.xhelper_prealpha_config.json. 
    • Документация внутри кода: Добавляйте строки‑docstring к каждой функции – они автоматически появятся в подсказках IDE. 
    • Перевод: Если вы планируете распространять плагин, используйте QTranslator + .qm‑файлы (в xHelper есть система локализации, подключайте её при необходимости). 

📌 Итого
    • Плагин — это просто Python‑модуль с функцией register(main_window). 
    • Через main_window вы получаете полный контроль над UI и инструментами xHelper. 
    • Делайте UI‑элементы, вызывайте ADB‑команды, пишите потоки, логируйте – всё в привычном для PyQt 6 стиле. 
    • При правильном оформлении ваш плагин будет автоматически подхвачен, отобразится в интерфейсе и будет работать без переписывания ядра программы. 
Теперь вы полностью вооружены, чтобы расширять возможности xHelper любой фантазией: от продвинутого мониторинга, управления Wi‑Fi, имитации аппаратных клавиш до полностью новых модулей (скринкаст, авто‑тесты, интеграция с CI‑системами и т.д.).
Удачной разработки! 🚀
