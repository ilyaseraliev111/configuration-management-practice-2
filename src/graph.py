"""Обход графа в ширину очередью deque, без рекурсивных вызовов."""
from collections import deque
from dataclasses import dataclass, field
from src.config import ROOT_DEPTH
from src.dependencies import parse_dependency
from src.resolver import Resolver


@dataclass
class Graph:
    """Узлы имя=версия, рёбра, минимальные глубины и порядок открытия BFS."""
    root: str
    packages: dict = field(default_factory=dict)
    edges: dict = field(default_factory=dict)
    depths: dict = field(default_factory=dict)
    order: list = field(default_factory=list)

    def add(self, package, depth):
        """Открывает новый узел один раз и запоминает его глубину."""
        self.packages[package.key] = package
        self.edges[package.key] = []
        self.depths[package.key] = depth
        self.order.append(package.key)


def build_graph(repository, root, max_depth):
    """Раскрывает только узлы глубины < max_depth; циклы сохраняет рёбрами."""
    if type(max_depth) is not int or max_depth < ROOT_DEPTH:
        raise ValueError("глубина графа должна быть целой и неотрицательной")
    resolver = Resolver(repository)
    graph = Graph(root.key)
    graph.add(root, ROOT_DEPTH)
    queue = deque([root])
    while queue:
        package = queue.popleft()
        depth = graph.depths[package.key]
        if depth >= max_depth:
            continue
        for raw in package.dependencies:
            dependency = parse_dependency(raw)
            if dependency.conflict:
                continue
            child = resolver.resolve(dependency)
            if child.key not in graph.edges[package.key]:
                graph.edges[package.key].append(child.key)
            if child.key not in graph.depths:
                graph.add(child, depth + 1)
                queue.append(child)
    return graph
