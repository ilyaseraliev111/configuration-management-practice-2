"""Строгая схема JSON-репозитория, имена A-Z и диагностируемые ошибки."""
import json
from pathlib import Path
import tempfile
import unittest
from src.json_repository import load_test_repository


class JSONTests(unittest.TestCase):
    """Тестовый граф не должен молча терять ключи, версии или зависимости."""

    def load_text(self, text):
        """Читает временный файл с пробелом в имени и UTF-8 BOM."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test graph.json"
            path.write_text(text, encoding="utf-8-sig")
            return load_test_repository(path)

    def test_good(self):
        """Правильный пустой список зависимостей допустим."""
        data = {"packages": [{"name": "A", "version": "1.0-r0",
                              "dependencies": []}]}
        repo = self.load_text(json.dumps(data))
        self.assertEqual(repo.exact("A", "1.0-r0").dependencies, ())

    def test_bad_structure(self):
        """Проверяет типы корня, массива и записей, а также лишние поля."""
        for data in [[], {}, {"packages": {}}, {"packages": []},
                     {"packages": [1]}, {"packages": [{"name": "A"}]},
                     {"packages": [], "extra": 1}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    self.load_text(json.dumps(data))

    def test_bad_values(self):
        """Проверяет имена, версии, тип массива зависимостей и его элементы."""
        for key, value in [("name", "lower"), ("name", "A1"),
                           ("version", "latest"), ("dependencies", "B"),
                           ("dependencies", [1]), ("dependencies", ["b"])]:
            record = {"name": "A", "version": "1", "dependencies": []}
            record[key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    self.load_text(json.dumps({"packages": [record]}))

    def test_duplicates_and_syntax(self):
        """Повтор ключа и повтор имя=версия не затираются последней записью."""
        duplicate = {"name": "A", "version": "1", "dependencies": []}
        texts = ['{"packages":[],"packages":[]}', "{invalid",
                 json.dumps({"packages": [duplicate, duplicate]})]
        for text in texts:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    self.load_text(text)
