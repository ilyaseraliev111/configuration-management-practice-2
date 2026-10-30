"""Полный путь CLI этапа 3: тестовый файл, HTTP, stderr и граница глубины."""
import contextlib
import io
from pathlib import Path
import unittest
from examples.http_fixture import repository_server
from src.main import main

REPOS = Path(__file__).resolve().parents[1] / "examples" / "repos"
SUCCESS = 0
RUNTIME_ERROR = 1


def execute(args):
    """Запускает main с перехватом обоих потоков и кода завершения."""
    output, error = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(output):
        with contextlib.redirect_stderr(error):
            code = main(args)
    return code, output.getvalue(), error.getvalue()


class GraphCLITests(unittest.TestCase):
    """Отладочный вывод настроек не должен заменять результат графа."""

    def test_json_cycle_and_ascii(self):
        """Цикл завершается и сохраняет обратное ребро; дерева пока нет."""
        code, output, error = execute([
            "--package", "A", "--version", "1.0-r0", "--test-repo",
            "--repository", str(REPOS / "cycle.json"), "--max-depth", "9",
            "--ascii"])
        self.assertEqual(code, SUCCESS)
        self.assertIn("C=1.0-r0 -> A=1.0-r0", output)
        self.assertNotIn("repository=", output)
        self.assertIn("этапом 5", error)

    def test_zero_depth(self):
        """Глубина 0 показывает только корень и не ищет отсутствующий Z."""
        code, output, error = execute([
            "--package", "A", "--version", "1.0-r0", "--test-repo",
            "--repository", str(REPOS / "missing_dependency.json"),
            "--max-depth", "0"])
        self.assertEqual(code, SUCCESS)
        self.assertIn("0\tA=1.0-r0", output)
        self.assertNotIn("Z=", output)
        self.assertEqual(error, "")

    def test_graph_errors(self):
        """Ошибки данных или корневой версии дают stderr и код 1."""
        for filename, version in [("missing_dependency.json", "1.0-r0"),
                                  ("invalid_schema.json", "1.0-r0"),
                                  ("chain.json", "9.0-r0")]:
            code, output, error = execute([
                "--package", "A", "--version", version, "--test-repo",
                "--repository", str(REPOS / filename)])
            with self.subTest(filename=filename):
                self.assertEqual(code, RUNTIME_ERROR)
                self.assertEqual(output, "")
                self.assertIn("Ошибка:", error)
                self.assertNotIn("Traceback", error)

    def test_real_format_http(self):
        """Пакет через HTTP раскрывается в реального поставщика so:libc."""
        with repository_server() as source:
            code, output, error = execute([
                "--package", "busybox", "--version", "1.37.0-r20",
                "--repository", source])
        self.assertEqual(code, SUCCESS)
        self.assertIn("busybox=1.37.0-r20 -> musl=1.2.5-r13", output)
        self.assertEqual(error, "")
