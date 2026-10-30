"""Вывод прямых зависимостей этапа 2 и общие ошибки реального источника."""
import contextlib
import io
import unittest
from src.main import main
from src.config import parse_config
from src.display import note_reserved_ascii, print_direct
from src.remote import load_remote
from examples.http_fixture import repository_server

SUCCESS = 0
RUNTIME_ERROR = 1


class DirectTests(unittest.TestCase):
    """Сохраняет проверку вывода этапа 2 после добавления обхода BFS."""

    def test_direct_output(self):
        """Функция вывода этапа 2 сохраняет исходные ограничения поля D."""
        with repository_server() as source:
            output, error = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output):
                with contextlib.redirect_stderr(error):
                    config = parse_config(["--package", "busybox",
                                           "--version", "1.36.1-r8",
                                           "--repository", source, "--ascii"])
                    repo = load_remote(config.repository)
                    print_direct(repo.exact(config.package, config.version))
                    note_reserved_ascii(config)
        self.assertIn("musl>=1.2", output.getvalue())
        self.assertNotIn("repository=", output.getvalue())
        self.assertIn("этапом 5", error.getvalue())

    def test_runtime_errors(self):
        """Пакет или версия не найдены: stderr и код 1 без traceback."""
        with repository_server() as source:
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                result = main(["--package", "busybox", "--version",
                               "9.9-r0", "--repository", source])
        self.assertEqual(result, RUNTIME_ERROR)
        self.assertIn("не найден", error.getvalue())
