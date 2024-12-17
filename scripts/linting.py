""" Модуль для запуска проверок кода. Запускает разные линтеры. """

import subprocess
import sys
from pathlib import Path


def run_command(command):
    """
    Функция для запуска команды.
    """
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, check=False
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


def main():
    """
    Функция для запуска линтеров.
    """
    src_path = Path(".").absolute()
    exit_code = 0

    commands = [
        f"black {src_path} --quiet",
        f"isort {src_path}",
        f"mypy {src_path}",
        f"pylint {src_path} --disable=too-few-public-methods",
        f"flake8 {src_path} --ignore E501",
    ]

    for cmd in commands:
        current_exit_code = run_command(cmd)
        exit_code = max(exit_code, current_exit_code)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
