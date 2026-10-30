"""Текстовый вывод этапов до графической визуализации."""
import sys


def print_direct(package):
    """Только этап 2: печатает все исходные ограничения поля D."""
    print(f"Прямые зависимости {package.key}:")
    if not package.dependencies:
        print("  (нет)")
    for dependency in package.dependencies:
        print(f"  {dependency}")


def note_reserved_ascii(config):
    """Поясняет отложенный флаг, не реализуя визуализацию этапа 5."""
    if config.ascii:
        print("Флаг --ascii сохранён; вывод дерева предусмотрен этапом 5.",
              file=sys.stderr)
