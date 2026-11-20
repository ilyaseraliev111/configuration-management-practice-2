"""Формат прямых зависимостей для проверки второго этапа."""


def print_direct(package):
    """Только этап 2: печатает все исходные ограничения поля D."""
    print(f"Прямые зависимости {package.key}:")
    if not package.dependencies:
        print("  (нет)")
    for dependency in package.dependencies:
        print(f"  {dependency}")
