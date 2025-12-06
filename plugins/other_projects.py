# -*- coding: utf-8 -*-
"""
other_projects – очень простой плагин для xHelper α‑1.0.1 LTS/ATS.

* Что делает
  – добавляет в строку меню (после пункта «Вид») новый пункт **«Наши другие проекты»**;
  – в выпадающем меню три ссылки:
        1) Runget telegram channel               → https://t.me/runget_rt
        2) Dual gaming centre telegram channel  → https://t.me/DGC_off
        3) dual gaming centre                   → https://kolyadual.github.io/dualgamingcentre/
  – при нажатию ссылка открывается в системном браузере
  – всё происходит через объект `main_window`; в лог пишется небольшое подтверждение.

* Почему так просто
  – в xHelper нет собственного `QToolBar`, поэтому проще работать с `QMenuBar`;
  – импортируем только необходимые классы (`QAction`, `QMenu`, `QUrl`, `QDesktopServices`);
  – проверяем, не добавлен ли уже пункт, чтобы при повторной загрузке не получать дублей.
"""

# -------------------------------------------------------------
#   Импорт только того, что реально используется
# -------------------------------------------------------------
from PyQt6.QtWidgets import QAction, QMenu          # элементы меню
from PyQt6.QtCore    import QUrl                   # URL‑объекты
from PyQt6.QtGui     import QDesktopServices       # открытие в браузере


# -------------------------------------------------------------
#   Вспомогательная функция – создаёт действие‑ссылку
# -------------------------------------------------------------
def _add_link(menu: QMenu, title: str, url: str) -> None:
    """
    Добавляет в ``menu`` QAction с подписью ``title``.
    При срабатывании (clicked) открывается ``url`` в системном браузере.
    """
    act = QAction(title, menu)
    # λ‑функция захватывает текущий ``url`` через параметр‑по‑умолчанию
    act.triggered.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))   # noqa: E731
    menu.addAction(act)


# -------------------------------------------------------------
#   Точка входа плагина
# -------------------------------------------------------------
def register(main_window):
    """
    main_window – уже инициализированный объект XHelperMainWindow.
    Функция вызывается один раз при загрузке плагинов.
    """
    # -----------------------------------------------------------------
    # 1. Защита от двойного добавления (может произойти при
    #    перезапуске окна без полной перезагрузки программы)
    # -----------------------------------------------------------------
    for act in main_window.menuBar().actions():
        if act.text() == "Наши другие проекты":
            main_window.log_message("[OtherProjects] Меню уже существует – пропуск.")
            return

    # -----------------------------------------------------------------
    # 2. Создаём собственное меню и заполняем его ссылками
    # -----------------------------------------------------------------
    proj_menu = QMenu("Наши другие проекты", main_window)

    _add_link(proj_menu, "Runget telegram channel",               "https://t.me/runget_rt")
    _add_link(proj_menu, "Dual gaming centre telegram channel",    "https://t.me/DGC_off")
    _add_link(proj_menu, "dual gaming centre",                    "https://kolyadual.github.io/dualgamingcentre/")

    # -----------------------------------------------------------------
    # 3. Вставляем новое меню после пункта «Вид», если он есть.
    # -----------------------------------------------------------------
    menubar = main_window.menuBar()
    view_action = None
    for act in menubar.actions():
        if act.text() == "Вид":
            view_action = act
            break

    if view_action:
        # Позиция действия «Вид» в текущем списке
        actions = menubar.actions()
        idx = actions.index(view_action)

        # Действие, которое следует сразу за «Вид», может не существовать
        after_action = actions[idx + 1] if idx + 1 < len(actions) else None

        if after_action:
            # insertMenu вставляет **перед** переданным действием,
            # поэтому вставляем перед after_action → получаем позицию «после Вид».
            menubar.insertMenu(after_action, proj_menu)
        else:
            # «Вид» был последним пунктом – просто добавляем в конец
            menubar.addMenu(proj_menu)
    else:
        # Если почему‑то в меню нет «Вид», добавляем в конец без разборов
        menubar.addMenu(proj_menu)

    # -----------------------------------------------------------------
    # 4. Записываем в общий лог, чтобы пользователь видел, что всё ок
    # -----------------------------------------------------------------
    main_window.log_message("[OtherProjects] Пункт меню «Наши другие проекты» добавлен.")
