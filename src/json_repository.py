"""Загрузка тестового JSON-графа с пакетами из больших латинских букв."""
import json
from pathlib import Path
from src.dependencies import parse_dependency
from src.repository import Package, Repository
from src.validation import validate_name, validate_version

PACKAGE_FIELDS = {"name", "version", "dependencies"}


def unique_keys(pairs):
    """Не допускает неявного затирания дублированных ключей в JSON."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"повторный ключ JSON: {key}")
        result[key] = value
    return result


def test_package(record):
    """Проверяет схему записи и ограничения зависимостей A–Z."""
    if not isinstance(record, dict) or set(record) != PACKAGE_FIELDS:
        raise ValueError("запись пакета: нужны name, version, dependencies")
    name = validate_name(record["name"], test_mode=True)
    version = validate_version(record["version"])
    dependencies = record["dependencies"]
    if not isinstance(dependencies, list):
        raise ValueError(f"{name}: dependencies должен быть массивом")
    for raw in dependencies:
        validate_name(parse_dependency(raw).name, test_mode=True)
    return Package(name, version, tuple(dependencies))


def load_test_repository(source):
    """Читает UTF-8/UTF-8 BOM JSON, сохраняя версии и направление рёбер."""
    try:
        data = json.loads(Path(source).read_text(encoding="utf-8-sig"),
                          object_pairs_hook=unique_keys)
    except (json.JSONDecodeError, RecursionError) as error:
        raise ValueError(f"неверный JSON тестового репозитория: {error}") \
            from error
    if not isinstance(data, dict) or set(data) != {"packages"}:
        raise ValueError("корень JSON должен содержать только массив packages")
    if not isinstance(data["packages"], list):
        raise ValueError("packages должен быть массивом")
    return Repository(test_package(record) for record in data["packages"])
