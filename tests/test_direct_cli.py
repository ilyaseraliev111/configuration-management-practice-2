"""Интеграционные проверки приложения этапа 2 на локальном HTTP."""
import contextlib
import io
import unittest
from src.main import main
from examples.http_fixture import repository_server

SUCCESS = 0
RUNTIME_ERROR = 1


class DirectTests(unittest.TestCase):
    """CLI должен выводить зависимости выбранной версии, а не параметры."""

    def test_direct_output(self):
        """Выбирает версию, не печатает настройки и поясняет флаг ASCII."""
        with repository_server() as source:
            output, error = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output):
                with contextlib.redirect_stderr(error):
                    result = main(["--package", "busybox", "--version",
                                   "1.36.1-r8", "--repository", source,
                                   "--ascii"])
        self.assertEqual(result, SUCCESS)
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
