"""Проверка имён пакетов, версий APK и адресов источника."""
from pathlib import Path
import re
from urllib.parse import urlsplit

PACKAGE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+\-]*")
TEST_NAME = re.compile(r"[A-Z]+")
VERSION = re.compile(
    r"[0-9]+(?:\.[0-9]+)*[a-z]?"
    r"(?:_(?:alpha|beta|pre|rc|cvs|svn|git|hg|p)[0-9]*)*"
    r"(?:~[0-9a-f]+)?(?:-r[0-9]+)?"
)
MIN_PORT = 1
MAX_PORT = 65535


def validate_name(value, test_mode=False):
    """Разрешает имена APK или только большие латинские буквы для тестов."""
    pattern = TEST_NAME if test_mode else PACKAGE_NAME
    if not isinstance(value, str) or not pattern.fullmatch(value):
        rule = "большие латинские буквы A-Z" if test_mode else "имя APK"
        raise ValueError(f"неверное имя пакета {value!r}: требуется {rule}")
    return value


def validate_version(value):
    """Проверяет синтаксис версии Alpine, включая суффиксы и ревизию."""
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError(f"неверная версия APK: {value!r}")
    return value


def validate_url(value):
    """Проверяет HTTP(S)-адрес каталога или APKINDEX.tar.gz."""
    if not value or any(char.isspace() for char in value):
        raise ValueError("URL репозитория пуст или содержит пробелы")
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("репозиторий должен иметь URL http:// или https://")
    if any((parts.username, parts.password, parts.query, parts.fragment)):
        raise ValueError("URL не должен содержать пароль, query или fragment")
    port = parts.port
    if port is not None and not MIN_PORT <= port <= MAX_PORT:
        raise ValueError("неверный порт URL")
    return value


def validate_source(value, test_mode=False):
    """Проверяет URL либо существующий файл тестового JSON-репозитория."""
    if test_mode:
        if not value or not Path(value).is_file():
            raise ValueError("--repository: нужен существующий файл тестов")
        return value
    return validate_url(value)
