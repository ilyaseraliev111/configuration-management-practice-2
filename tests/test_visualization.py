"""Проверки Mermaid и ASCII для циклов, ромба и длинной цепочки."""
import unittest

from src.graph import build_graph
from src.repository import Package, Repository
from src.visualization import ascii_lines, mermaid_lines
from test_graph import DEEP_NODE_COUNT, graph_from


class VisualizationTests(unittest.TestCase):
    """Форматы вывода сохраняют версии и связи без рекурсии."""

    def test_mermaid_cycle(self):
        """Циклическое ребро выводится явно и не дублирует узлы."""
        self.assertEqual(list(mermaid_lines(graph_from("cycle.json"))), [
            "flowchart TD",
            '    n0["A=1.0-r0"]',
            '    n1["B=1.0-r0"]',
            '    n2["C=1.0-r0"]',
            "    n0 --> n1",
            "    n1 --> n2",
            "    n2 --> n0",
        ])

    def test_ascii_diamond(self):
        """Дерево повторно ссылается на общий пакет D."""
        self.assertEqual(list(ascii_lines(graph_from("diamond.json"))), [
            "A=1.0-r0",
            "|-- B=1.0-r0",
            "|   `-- D=1.0-r0",
            "`-- C=1.0-r0",
            "    `-- D=1.0-r0 [shared]",
        ])

    def test_ascii_self_cycle(self):
        """Петля представляется ссылкой на корневой узел."""
        self.assertEqual(list(ascii_lines(graph_from("self_cycle.json"))), [
            "A=1.0-r0", "`-- A=1.0-r0 [cycle]",
        ])

    def test_versions_are_distinct(self):
        """У разных версий одного имени остаются разные вершины Mermaid."""
        root = Package("A", "1", ("B=1", "B=2"))
        repo = Repository([root, Package("B", "1"), Package("B", "2")])
        lines = list(mermaid_lines(build_graph(repo, root, 1)))
        self.assertIn('    n1["B=1"]', lines)
        self.assertIn('    n2["B=2"]', lines)

    def test_ascii_deep_chain(self):
        """Дерево из 1500 узлов выводится без переполнения стека Python."""
        packages = [Package(f"P{i}", "1", (f"P{i + 1}",))
                    for i in range(DEEP_NODE_COUNT - 1)]
        last = Package(f"P{DEEP_NODE_COUNT - 1}", "1")
        packages.append(last)
        graph = build_graph(Repository(packages), packages[0], DEEP_NODE_COUNT)
        lines = list(ascii_lines(graph))
        self.assertEqual(len(lines), DEEP_NODE_COUNT)
        self.assertTrue(lines[-1].endswith(last.key))
