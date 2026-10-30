"""Общие функции автоматических демонстраций; менеджеры пакетов не нужны."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUCCESS = 0
ARGUMENT_ERROR = 2
RUNTIME_ERROR = 1


def run_case(args, expected=SUCCESS, fragment=""):
    """Печатает запуск и результат, проверяет код и обязательный фрагмент."""
    command = [sys.executable, "-m", "src.main", *args]
    print("\n> " + subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", env=utf8_environment())
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    if result.returncode != expected:
        raise AssertionError(f"Код {result.returncode}, ожидался {expected}")
    if fragment not in result.stdout + result.stderr:
        raise AssertionError(f"Нет ожидаемого фрагмента: {fragment}")
    print(f"PASS: код {expected}", flush=True)
    return result.stdout


def utf8_environment():
    """Обеспечивает одинаковое декодирование дочернего Python в Windows."""
    import os

    return {**os.environ, "PYTHONUTF8": "1"}
