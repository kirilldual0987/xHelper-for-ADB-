#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xHelper 2.0 Release installer.

Creates a local Python virtual environment, installs runtime dependencies,
creates launch scripts, and optionally creates desktop shortcuts for the
current user. Run from the unpacked xHelper 2.0 Release project directory:

    python install_xhelper_2_0.py
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "xHelper 2.0 Release"
MAIN_SCRIPT = "xHelper 2.0 Release.py"
VENV_DIR = ".venv-xhelper-2.0"
REQUIREMENTS = ["PyQt6"]


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("→", " ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def project_dir() -> Path:
    return Path(__file__).resolve().parent


def venv_python(root: Path) -> Path:
    if platform.system() == "Windows":
        return root / VENV_DIR / "Scripts" / "python.exe"
    return root / VENV_DIR / "bin" / "python"


def ensure_main_script(root: Path) -> Path:
    main = root / MAIN_SCRIPT
    if not main.exists():
        raise FileNotFoundError(f"Не найден основной файл {MAIN_SCRIPT!r} в {root}")
    return main


def create_venv(root: Path) -> Path:
    py = venv_python(root)
    if not py.exists():
        print(f"Создаю виртуальное окружение {VENV_DIR}...")
        run([sys.executable, "-m", "venv", VENV_DIR], cwd=root)
    else:
        print(f"Виртуальное окружение уже существует: {py}")
    return py


def install_dependencies(py: Path) -> None:
    print("Обновляю pip и устанавливаю зависимости xHelper 2.0 Release...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", *REQUIREMENTS])


def warn_external_tools() -> None:
    missing = []
    for tool in ("adb", "fastboot"):
        if shutil.which(tool) is None:
            missing.append(tool)
    if missing:
        print("\nВНИМАНИЕ: не найдены в PATH:", ", ".join(missing))
        print(
            "Установите Android Platform Tools или укажите пути в ~/.xhelper_config.json."
        )
    if shutil.which("scrcpy") is None:
        print(
            "Подсказка: scrcpy не найден. Зеркалирование экрана будет недоступно до его установки."
        )


def create_launchers(root: Path, py: Path, main: Path) -> None:
    if platform.system() == "Windows":
        launcher = root / "run_xhelper_2_0_release.bat"
        launcher.write_text(
            f'@echo off\r\n"{py}" "{main}" %*\r\n',
            encoding="utf-8",
        )
    else:
        launcher = root / "run_xhelper_2_0_release.sh"
        launcher.write_text(
            f'#!/usr/bin/env sh\n"{py}" "{main}" "$@"\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
    print(f"Создан запускатель: {launcher}")


def create_desktop_shortcut(root: Path, py: Path, main: Path) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
            shortcut = desktop / "xHelper 2.0 Release.bat"
            shortcut.write_text(
                f'@echo off\r\ncd /d "{root}"\r\n"{py}" "{main}" %*\r\n',
                encoding="utf-8",
            )
            print(f"Создан ярлык на рабочем столе: {shortcut}")
        elif system == "Linux":
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                shortcut = desktop / "xhelper-2.0-release.desktop"
                shortcut.write_text(
                    "\n".join(
                        [
                            "[Desktop Entry]",
                            "Type=Application",
                            f"Name={APP_NAME}",
                            f"Exec={py} {main}",
                            f"Path={root}",
                            "Terminal=false",
                            "Categories=Utility;Development;",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                shortcut.chmod(0o755)
                print(f"Создан .desktop ярлык: {shortcut}")
            else:
                print("Рабочий стол Linux не найден, .desktop ярлык пропущен.")
        elif system == "Darwin":
            launcher = root / "run_xhelper_2_0_release.command"
            launcher.write_text(
                f'#!/usr/bin/env bash\ncd "{root}"\n"{py}" "{main}" "$@"\n',
                encoding="utf-8",
            )
            launcher.chmod(0o755)
            print(f"Создан macOS .command запускатель: {launcher}")
    except Exception as exc:
        print(f"Не удалось создать ярлык: {exc}")


def main() -> int:
    root = project_dir()
    print(f"Установка {APP_NAME} из: {root}")
    try:
        main_script = ensure_main_script(root)
        py = create_venv(root)
        install_dependencies(py)
        create_launchers(root, py, main_script)
        create_desktop_shortcut(root, py, main_script)
        warn_external_tools()
    except subprocess.CalledProcessError as exc:
        print(f"\nОшибка выполнения команды, код {exc.returncode}: {exc.cmd}")
        return exc.returncode or 1
    except Exception as exc:
        print(f"\nУстановка не завершена: {exc}")
        return 1

    print(
        "\nГотово. xHelper 2.0 Release установлен локально для текущего пользователя."
    )
    print(
        "Запуск: используйте созданный run_xhelper_2_0_release.* файл или ярлык на рабочем столе."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
