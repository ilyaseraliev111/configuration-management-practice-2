"""Порядок зависимостей, циклы, граница глубины и независимые ветви."""
import unittest
from src.loading import ensure_complete, loading_order
from src.graph import build_graph
from src.repository import Package, Repository
from test_graph import graph_from, DEEP_NODE_COUNT
from test_graph_cli import execute, REPOS


class LoadingTests(unittest.TestCase):
    """Проверяет условия порядка, а не только одну строку результата."""

    def test_chain(self):
        """Зависимости оказываются раньше корня, порядок обратен цепи BFS."""
        graph = graph_from("chain.json")
        self.assertEqual(loading_order(graph), list(reversed(graph.order)))

    def test_diamond(self):
        """Общий D загружается один раз, B и C сортируются стабильно."""
        graph = graph_from("diamond.json")
        order = loading_order(graph)
        self.assertEqual(order,
                         ["D=1.0-r0", "B=1.0-r0", "C=1.0-r0", "A=1.0-r0"])
        for parent, children in graph.edges.items():
            for child in children:
                self.assertLess(order.index(child), order.index(parent))

    def test_cycles(self):
        """Цикл и петля дают явную ошибку, а не ложный порядок."""
        for name in ["cycle.json", "self_cycle.json"]:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "цикл"):
                    loading_order(graph_from(name))

    def test_incomplete(self):
        """Усечённый граф нельзя выдавать за полный порядок загрузки."""
        from src.json_repository import load_test_repository

        repository = load_test_repository(REPOS / "chain.json")
        graph = build_graph(repository, repository.exact("A", "1.0-r0"), 1)
        with self.assertRaisesRegex(ValueError, "увеличьте --max-depth"):
            ensure_complete(graph, repository)

    def test_multiple_versions(self):
        """Нельзя молча выдать две версии одного пакета для загрузки."""
        root = Package("A", "1", ("B=1", "B=2"))
        repo = Repository([root, Package("B", "1"), Package("B", "2")])
        graph = build_graph(repo, root, 3)
        with self.assertRaisesRegex(ValueError, "несовместимые версии"):
            loading_order(graph)

    def test_deep_chain(self):
        """Сортировка также не использует рекурсию на цепи 1500 узлов."""
        packages = [Package(f"P{i}", "1", (f"P{i + 1}",))
                    for i in range(DEEP_NODE_COUNT - 1)]
        packages.append(Package(f"P{DEEP_NODE_COUNT - 1}", "1"))
        graph = build_graph(Repository(packages), packages[0], DEEP_NODE_COUNT)
        order = loading_order(graph)
        self.assertEqual(len(order), DEEP_NODE_COUNT)
        self.assertEqual(order[-1], "P0=1")

    def test_cli_modes(self):
        """Без флага остаётся BFS; с флагом выводится только порядок."""
        args = ["--package", "A", "--version", "1.0-r0", "--test-repo",
                "--repository", str(REPOS / "chain.json")]
        code, output, error = execute(args + ["--load-order"])
        self.assertEqual(code, 0)
        self.assertIn("1\tD=1.0-r0", output)
        self.assertNotIn("Пакеты (BFS", output)
        self.assertEqual(error, "")
        self.assertIn("Пакеты (BFS", execute(args)[1])

    def test_cli_error(self):
        """На цикле нет частичного плана, возвращается код ошибки 1."""
        code, output, error = execute([
            "--package", "A", "--version", "1.0-r0", "--test-repo",
            "--repository", str(REPOS / "cycle.json"), "--load-order"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("цикл", error)

    def test_disconnected(self):
        """Загрузка включает только достижимые от выбранного корня узлы."""
        self.assertEqual(loading_order(graph_from("disconnected.json")),
                         ["A=1.0-r0"])
