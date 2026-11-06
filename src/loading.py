"""Порядок загрузки: зависимости раньше зависимых, алгоритм Кана."""
from collections import defaultdict
import heapq
from src.dependencies import parse_dependency
from src.resolver import Resolver

NO_DEPENDENCIES = 0


def ensure_complete(graph, repository):
    """Запрещает выдавать порядок для усечённого глубиной графа."""
    resolver = Resolver(repository)
    for parent, package in graph.packages.items():
        for raw in package.dependencies:
            dependency = parse_dependency(raw)
            if dependency.conflict:
                continue
            child = resolver.resolve(dependency)
            if child.key not in graph.edges[parent]:
                raise ValueError("граф усечён: увеличьте --max-depth "
                                 "для полного порядка загрузки")


def check_versions(graph):
    """Отклоняет граф, требующий разные версии одного реального пакета."""
    selected = {}
    for package in graph.packages.values():
        previous = selected.setdefault(package.name, package.version)
        if previous != package.version:
            raise ValueError(f"несовместимые версии пакета {package.name}")


def schedule_inputs(graph):
    """Считает зависимости и строит обратные рёбра для алгоритма Кана."""
    remaining = {key: len(children) for key, children in graph.edges.items()}
    dependents = defaultdict(list)
    for parent, children in graph.edges.items():
        for child in children:
            dependents[child].append(parent)
    return remaining, dependents


def loading_order(graph):
    """Сортирует DAG итеративно; цикл не имеет линейного порядка загрузки."""
    check_versions(graph)
    remaining, dependents = schedule_inputs(graph)
    ready = [key for key, count in remaining.items()
             if count == NO_DEPENDENCIES]
    heapq.heapify(ready)
    result = []
    while ready:
        key = heapq.heappop(ready)
        result.append(key)
        for parent in dependents[key]:
            remaining[parent] -= 1
            if remaining[parent] == NO_DEPENDENCIES:
                heapq.heappush(ready, parent)
    if len(result) != len(graph.packages):
        blocked = sorted(key for key, count in remaining.items() if count)
        raise ValueError("цикл: линейный порядок невозможен; "
                         "не упорядочены: " + ", ".join(blocked))
    return result


def print_loading_order(graph, repository):
    """Проверяет полноту, затем печатает порядок с включённым корнем."""
    ensure_complete(graph, repository)
    order = loading_order(graph)
    print("Порядок загрузки (зависимости перед пакетом):")
    for number, key in enumerate(order, start=1):
        print(f"{number}\t{key}")
