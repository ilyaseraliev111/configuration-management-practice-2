"""Выбор версий и поставщиков библиотек без системного APK solver."""
import unittest
from src.dependencies import parse_dependency
from src.graph import build_graph
from src.repository import Package, Repository
from src.resolver import Resolver


class ResolverTests(unittest.TestCase):
    """Проверяет ограничения имени, версии и виртуальных provides."""

    def test_newest_matching(self):
        """Выбирает новейшую подходящую версию с числовым сравнением."""
        repo = Repository([Package("B", "1.9"), Package("B", "1.10"),
                           Package("B", "2.0")])
        resolver = Resolver(repo)
        result = resolver.resolve(parse_dependency("B<2.0"))
        self.assertEqual(result.version, "1.10")
        with self.assertRaises(ValueError):
            resolver.resolve(parse_dependency("B>9.0"))

    def test_provided_version(self):
        """Ограничение проверяется по версии ABI, а не по версии пакета."""
        package = Package("library", "9.0-r1", provides=("so:lib.so=2",))
        resolver = Resolver(Repository([package]))
        self.assertEqual(resolver.resolve(parse_dependency("so:lib.so<3")),
                         package)
        with self.assertRaises(ValueError):
            resolver.resolve(parse_dependency("so:lib.so>3"))

    def test_primary_and_priority(self):
        """Реальное имя предпочтительнее alias; приоритет выбирает provider."""
        packages = [Package("A", "1"),
                    Package("B", "9", provides=("A=9",)),
                    Package("C", "1", provides=("virtual=1",), priority=10),
                    Package("D", "1", provides=("virtual=1",), priority=20)]
        resolver = Resolver(Repository(packages))
        self.assertEqual(resolver.resolve(parse_dependency("A")).name, "A")
        self.assertEqual(resolver.resolve(parse_dependency("virtual")).name,
                         "D")

    def test_unversioned_provider(self):
        """Alias без версии требует приоритета и не удовлетворяет >=1."""
        package = Package("A", "1", provides=("virtual",), priority=10)
        resolver = Resolver(Repository([package]))
        self.assertEqual(resolver.resolve(parse_dependency("virtual")),
                         package)
        with self.assertRaises(ValueError):
            resolver.resolve(parse_dependency("virtual>=1"))
        resolver = Resolver(Repository([Package("A", "1", provides=("v",))]))
        with self.assertRaises(ValueError):
            resolver.resolve(parse_dependency("v"))

    def test_conflicts_are_not_edges(self):
        """!B не требует загрузки B и не создаёт ложное ребро графа."""
        root = Package("A", "1", ("!B", "C"))
        repo = Repository([root, Package("C", "1")])
        graph = build_graph(repo, root, 3)
        self.assertEqual(graph.order, ["A=1", "C=1"])

    def test_bad_provides(self):
        """Неправильные ограничения в поле p отклоняются."""
        for raw in ["!B", "B>=1"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    Resolver(Repository([Package("A", "1", provides=(raw,))]))
