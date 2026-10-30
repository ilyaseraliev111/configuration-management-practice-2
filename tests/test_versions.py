"""Порядок версий APK и ограничения; не SemVer-сортировка строк."""
import unittest
from src.dependencies import parse_dependency
from src.validation import validate_version
from src.versions import (EQUAL, GREATER, LESS, compare_versions,
                          matches_version)


class VersionTests(unittest.TestCase):
    """Ревизии, prerelease, предоставляемые версии и ошибки синтаксиса."""

    def test_numeric_and_revision(self):
        """Числа сравниваются численно, а -r — отдельная ревизия APK."""
        for first, second in [("1.9", "1.10"), ("1.0-r2", "1.0-r10"),
                              ("1.0", "1.0.1"), ("1.0a", "1.0b"),
                              ("1.0~1234", "1.0~2345")]:
            with self.subTest(first=first, second=second):
                self.assertEqual(compare_versions(first, second), LESS)
                self.assertEqual(compare_versions(second, first), GREATER)
                self.assertEqual(compare_versions(first, first), EQUAL)

    def test_suffix_order(self):
        """Суффиксы до релиза меньше, cvs/git/p после релиза — больше."""
        versions = ["1.0_alpha1", "1.0_beta1", "1.0_pre1", "1.0_rc1",
                    "1.0", "1.0_cvs1", "1.0_svn1", "1.0_git1", "1.0_p1"]
        for first, second in zip(versions, versions[1:]):
            self.assertEqual(compare_versions(first, second), LESS)

    def test_leading_zero(self):
        """Ведущие нули после точки сохраняют особое строковое правило APK."""
        self.assertEqual(compare_versions("8.2.0015", "8.2.002"), LESS)
        self.assertEqual(compare_versions("8.2.0", "8.2.001"), LESS)

    def test_constraints(self):
        """Проверяет точные, интервальные и префиксные ограничения."""
        for operator in [">", ">=", "<", "<=", "=", "~", "<~", ">~"]:
            self.assertIsInstance(matches_version("2.0", operator, "1.0"),
                                  bool)
        self.assertTrue(matches_version("1.2.9-r3", "~", "1.2"))
        self.assertFalse(matches_version("1.20", "~", "1.2"))
        self.assertTrue(matches_version("2.0-r0", ">=", "2.0"))
        self.assertFalse(matches_version("1.0", ">", "1.0"))
        with self.assertRaises(ValueError):
            matches_version("1.0", "!=", "2.0")

    def test_invalid_versions(self):
        """Отклоняет неподдерживаемые суффиксы и неправильные ревизии."""
        for version in ["latest", "", "1.0bc", "1.0a1", "1.0_foo", "1.0-r",
                        "1.0-r1-r2", "1.0~xyz", "v1.0"]:
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    validate_version(version)

    def test_dependency_atoms(self):
        """Проверяет конфликт, namespace, оператор и предоставляемую версию."""
        atom = parse_dependency("!so:libdemo.so.1>=2.0")
        self.assertTrue(atom.conflict)
        self.assertEqual(atom.name, "so:libdemo.so.1")
        self.assertEqual(atom.operator, ">=")
        self.assertEqual(atom.version, "2.0")
        for raw in ["", "A>>2", "A=", "bad name", 1]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_dependency(raw)
