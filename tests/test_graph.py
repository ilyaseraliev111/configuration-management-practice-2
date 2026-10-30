"""BFS, глубина, общие узлы, циклы и длинная цепь без рекурсии."""
from pathlib import Path
import unittest
from src.graph import build_graph
from src.json_repository import load_test_repository
from src.repository import Package, Repository

REPOS = Path(__file__).resolve().parents[1] / "examples" / "repos"
DEEP_NODE_COUNT = 1500


def graph_from(name, depth=3, version="1.0-r0"):
    """Строит граф примера от A с заданной версией и глубиной."""
    repository = load_test_repository(REPOS / name)
    root = repository.exact("A", version)
    return build_graph(repository, root, depth)


class GraphTests(unittest.TestCase):
    """Корень имеет глубину 0, каждое ребро ведёт к зависимости."""

    def test_depth_boundaries(self):
        """Нулевая глубина не раскрывает корень; граница включается в узлы."""
        for depth, count in [(0, 1), (1, 2), (2, 3), (3, 4)]:
            graph = graph_from("chain.json", depth)
            with self.subTest(depth=depth):
                self.assertEqual(len(graph.order), count)
                self.assertEqual(max(graph.depths.values()), depth)
                self.assertEqual(graph.edges[graph.order[-1]], [])

    def test_diamond(self):
        """Общий D открывается один раз, оба входящих ребра сохраняются."""
        graph = graph_from("diamond.json")
        self.assertEqual(graph.order,
                         ["A=1.0-r0", "B=1.0-r0", "C=1.0-r0", "D=1.0-r0"])
        self.assertEqual(graph.edges["B=1.0-r0"], ["D=1.0-r0"])
        self.assertEqual(graph.edges["C=1.0-r0"], ["D=1.0-r0"])
        self.assertEqual(graph.depths["D=1.0-r0"], 2)

    def test_cycles(self):
        """Цикл и петля завершаются; замыкающее ребро не теряется."""
        graph = graph_from("cycle.json", 100)
        self.assertEqual(len(graph.order), 3)
        self.assertEqual(graph.edges["C=1.0-r0"], ["A=1.0-r0"])
        loop = graph_from("self_cycle.json", 100)
        self.assertEqual(loop.order, ["A=1.0-r0"])
        self.assertEqual(loop.edges["A=1.0-r0"], ["A=1.0-r0"])

    def test_disconnected(self):
        """Необходные компоненты не включаются в граф выбранного корня."""
        graph = graph_from("disconnected.json")
        self.assertEqual(graph.order, ["A=1.0-r0"])

    def test_versions(self):
        """Версия корня меняет нужную ветвь зависимостей."""
        old = graph_from("versions.json")
        new = graph_from("versions.json", version="2.0-r0")
        self.assertIn("B=1.5-r0", old.order)
        self.assertNotIn("B=2.5-r0", old.order)
        self.assertIn("B=2.5-r0", new.order)

    def test_missing_only_when_expanded(self):
        """Отсутствующая зависимость обнаруживается только при раскрытии."""
        self.assertEqual(len(graph_from("missing_dependency.json", 0).order),
                         1)
        with self.assertRaisesRegex(ValueError, "не найдена зависимость: Z"):
            graph_from("missing_dependency.json", 1)

    def test_deep_chain(self):
        """1500 узлов превышают обычный предел рекурсии Python."""
        packages = [Package(f"P{i}", "1", (f"P{i + 1}",))
                    for i in range(DEEP_NODE_COUNT - 1)]
        packages.append(Package(f"P{DEEP_NODE_COUNT - 1}", "1"))
        repository = Repository(packages)
        graph = build_graph(repository, packages[0], DEEP_NODE_COUNT)
        self.assertEqual(len(graph.order), DEEP_NODE_COUNT)
        self.assertEqual(max(graph.depths.values()), DEEP_NODE_COUNT - 1)

    def test_invalid_depth(self):
        """API также отклоняет отрицательную или нецелую глубину."""
        for depth in [-1, "2", True]:
            with self.subTest(depth=depth):
                with self.assertRaises(ValueError):
                    graph_from("chain.json", depth)
