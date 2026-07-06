# plugins/release_info.py
# -*- coding: utf-8 -*-

"""
release_info – плагин‑модуль, отображающий окно с информацией при
запуске xHelper 2.0 Release.

Содержание окна:
    • Текст: «Эта программа – release‑версия, используйте на свой страх и риск.
      Хотите начать использование Release‑версии?»
    • Кнопка **«Продолжить»** – закрывает окно и продолжает работу.
    • Кнопка **«Выход»** – закрывает приложение.
    • Кнопка **«Что изменилось?»** – открывает второе окно‑помощник,
      где перечислены основные изменения релиза и рекомендации по безопасной работе.

Плагин не меняет ядро программы и использует только публичный API
`main_window` (логирование, закрытие окна, таймеры)."""

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QMessageBox,
)


# ----------------------------------------------------------------------
#   Текст справки (можно расширить при необходимости)
# ----------------------------------------------------------------------
HELP_TEXT = """
<h2>✅ xHelper 2.0 Release</h2>
<p><b>xHelper 2.0</b> — стабильная release-сборка графической утилиты для ADB/fastboot.</p>
<ul>
<li>обновлена базовая конфигурация и сохранение настроек в <code>~/.xhelper_config.json</code>;</li>
<li>улучшена загрузка плагинов: предсказуемый порядок, изоляция ошибок, пропуск служебных файлов;</li>
<li>плагины могут использовать общий путь к ADB и выбранное устройство через публичный API главного окна;</li>
<li>обновлена документация по запуску, требованиям и разработке плагинов.</li>
</ul>
<p>Перед опасными операциями (удаление файлов, прошивка, восстановление) проверяйте выбранное устройство.</p>
"""


# ----------------------------------------------------------------------
#   Первое (модальное) окно – информация о релизе
# ----------------------------------------------------------------------
def _show_release_info(main_window):
    """Показывает краткую информацию о релизе после запуска main_window."""
    dialog = QDialog(main_window)
    dialog.setWindowTitle("xHelper 2.0 Release")
    dialog.setModal(True)
    dialog.resize(460, 200)

    layout = QVBoxLayout(dialog)

    # Текстовое сообщение
    msg = QLabel(
        "<b>xHelper 2.0 Release</b> готов к работе.<br><br>"
        "Открыть краткую информацию о релизе?"
    )
    msg.setWordWrap(True)
    layout.addWidget(msg)

    # Кнопки
    btn_layout = QHBoxLayout()
    btn_yes = QPushButton("Продолжить")
    btn_no = QPushButton("Выход")
    btn_what = QPushButton("Что изменилось?")
    btn_layout.addWidget(btn_yes)
    btn_layout.addWidget(btn_no)
    btn_layout.addStretch()
    btn_layout.addWidget(btn_what)
    layout.addLayout(btn_layout)

    # --------------------------------------------------------------
    #   Обработчики кнопок
    # --------------------------------------------------------------
    def _accept():
        # Пользователь согласился – просто закрываем окно.
        dialog.accept()

    def _reject():
        # Пользователь отказался – закрываем главное окно программы.
        reply = QMessageBox.question(
            dialog,
            "Выход",
            "Вы действительно хотите закрыть программу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            main_window.close()  # произвольное закрытие
        else:
            # Если пользователь передумал – оставляем окно открытым.
            return

    def _show_details():
        """Открывает второе окно с подробным описанием и гайдом."""
        details = QDialog(dialog)
        details.setWindowTitle("Что значит «Release‑версия»")
        details.resize(560, 620)

        d_layout = QVBoxLayout(details)

        # Текстовое поле (read‑only) – позволяет копировать при необходимости
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setHtml(HELP_TEXT)  # HTML‑разметка для красоты
        d_layout.addWidget(txt)

        # Кнопка «Закрыть»
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(details.accept)
        d_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        details.exec()  # модальное окно

    # Привязываем сигналы
    btn_yes.clicked.connect(_accept)
    btn_no.clicked.connect(_reject)
    btn_what.clicked.connect(_show_details)

    # Показ диалога
    dialog.exec()


# ----------------------------------------------------------------------
#   Регистрация плагина
# ----------------------------------------------------------------------
def register(main_window):
    """
    При загрузке плагина ставим таймер «singleShot», чтобы показать
    окно после того, как главное окно полностью построится.
    """
    # Запускаем через <<0>> мсек, чтобы гарантировать, что UI уже готов.
    QTimer.singleShot(0, lambda: _show_release_info(main_window))

    # Информируем в лог, что плагин активирован
    main_window.log_message(
        "[Release‑Warning] Плагин загружен – показ предупреждения о версии."
    )
