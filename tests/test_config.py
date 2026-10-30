"""Проверки шести опций, комбинаций режимов и ошибок CLI."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from src.config import parse_config
from src.main import main

ARGUMENT_ERROR = 2
PARAMETER_COUNT = 6


def base_args():
    """Возвращает новый список корректных обязательных параметров."""
    return ["--package", "busybox", "--repository", "https://example.org/apk",
            "--version", "1.0-r0"]


class ConfigTests(unittest.TestCase):
    """Неправильный ввод не должен доходить до анализа зависимостей."""

    def test_all_values(self):
        """Значения и флаги выводятся только в прототипе этапа 1."""
        config = parse_config(base_args() + ["--ascii", "--max-depth", "0"])
        self.assertTrue(config.ascii)
        self.assertFalse(config.test_repo)
        self.assertEqual(config.max_depth, 0)

    def test_invalid_arguments(self):
        """Каждый настраиваемый параметр имеет демонстрацию ошибки."""
        replacements = [("--package", "bad/name"), ("--version", "latest"),
                        ("--repository", "ftp://example.org"),
                        ("--repository", "https://"),
                        ("--repository", "http://host:wrong"),
                        ("--repository", "http://host:70000"),
                        ("--max-depth", "-1"), ("--max-depth", "abc")]
        for option, value in replacements:
            args = base_args()
            if option in args:
                args[args.index(option) + 1] = value
            else:
                args.extend([option, value])
            with self.subTest(option=option, value=value):
                self.assert_argument_error(args)
        for flag in ["--ascii", "--test-repo"]:
            self.assert_argument_error(base_args() + [flag, "maybe"])

    def assert_argument_error(self, args):
        """Требует стандартный код ошибки аргументов и понятный stderr."""
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            with self.assertRaises(SystemExit) as result:
                parse_config(args)
        self.assertEqual(result.exception.code, ARGUMENT_ERROR)
        self.assertIn("error:", output.getvalue())

    def test_required_and_unknown(self):
        """Обязательные параметры нельзя пропускать или сокращать."""
        for option in ["--package", "--repository", "--version"]:
            args = base_args()
            index = args.index(option)
            del args[index:index + 2]
            self.assert_argument_error(args)
        self.assert_argument_error(base_args() + ["--unknown"])
        self.assert_argument_error(base_args() + ["--max", "2"])

    def test_test_repository(self):
        """Тестовый путь может содержать пробелы; имена нужны в A-Z."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test graph.json"
            path.write_text('{"packages": []}', encoding="utf-8")
            args = ["--package", "A", "--version", "1.0-r0", "--test-repo",
                    "--repository", str(path)]
            self.assertTrue(parse_config(args).test_repo)
            args[args.index("--package") + 1] = "lowercase"
            self.assert_argument_error(args)
        self.assert_argument_error(args)

    def test_no_network_in_prototype(self):
        """Прототип проверяет синтаксис URL без сетевого запроса."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(base_args()), 0)
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), PARAMETER_COUNT)
        self.assertIn("test_repo=false", lines)
