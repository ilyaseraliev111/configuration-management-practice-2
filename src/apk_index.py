"""Самостоятельное чтение текстового формата Alpine APKINDEX v2."""
from src.repository import Package, Repository
from src.validation import validate_name, validate_version

FIELD_LENGTH = 1
MIN_PRIORITY = 0


def package_from_fields(fields):
    """Проверяет обязательные P/V и сохраняет зависимости D, provides p."""
    name = validate_name(fields.get("P", ""))
    version = validate_version(fields.get("V", ""))
    try:
        priority = int(fields.get("k", "0"))
    except ValueError as error:
        raise ValueError(f"неверный приоритет k пакета {name}") from error
    if priority < MIN_PRIORITY:
        raise ValueError(f"отрицательный приоритет k пакета {name}")
    return Package(name, version, tuple(fields.get("D", "").split()),
                   tuple(fields.get("p", "").split()), priority)


def parse_index(text):
    """Разбирает записи, разделённые пустой строкой; допускает CRLF."""
    packages, fields = [], {}
    for number, line in enumerate([*text.splitlines(), ""], start=1):
        if not line:
            if fields:
                packages.append(package_from_fields(fields))
                fields = {}
            continue
        key, separator, value = line.partition(":")
        if not separator or len(key) != FIELD_LENGTH or not key.isalpha():
            raise ValueError(f"APKINDEX: неверное поле, строка {number}")
        if key in fields:
            raise ValueError(f"APKINDEX: повтор поля {key}, строка {number}")
        fields[key] = value
    return Repository(packages)
