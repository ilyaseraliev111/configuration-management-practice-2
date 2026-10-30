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


def print_graph(graph):
    """Показывает список узлов BFS и рёбра; это ещё не Mermaid/ASCII-дерево."""
    print("Пакеты (BFS, глубина):")
    for key in graph.order:
        print(f"{graph.depths[key]}\t{key}")
    print("Рёбра (пакет -> зависимость):")
    for parent in graph.order:
        for child in graph.edges[parent]:
            print(f"{parent} -> {child}")
    if not any(graph.edges.values()):
        print("(рёбра не раскрыты или отсутствуют)")
