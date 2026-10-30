"""Разбор ограничений D и предоставляемых имён p из APKINDEX."""
from dataclasses import dataclass
import re
from src.validation import validate_version
from src.versions import RESULTS

ATOM = re.compile(
    r"(?P<conflict>!)?(?P<name>[A-Za-z0-9/][A-Za-z0-9._+:/,\[\]\-]*)"
    r"(?:(?P<operator>[<>=~]+)(?P<version>.+))?"
)


@dataclass(frozen=True)
class Dependency:
    """Исходное ограничение, имя, оператор, версия и признак конфликта."""
    raw: str
    name: str
    operator: str = ""
    version: str = ""
    conflict: bool = False


def parse_dependency(raw):
    """Не обрезает so:/cmd:; отрицательные ограничения помечает отдельно."""
    if not isinstance(raw, str):
        raise ValueError("зависимость должна быть строкой")
    match = ATOM.fullmatch(raw)
    if match is None:
        raise ValueError(f"неверная зависимость: {raw!r}")
    fields = match.groupdict()
    operator = fields["operator"] or ""
    version = fields["version"] or ""
    if operator not in RESULTS:
        raise ValueError(f"неподдерживаемое ограничение: {raw}")
    if operator:
        validate_version(version)
    return Dependency(raw, fields["name"], operator, version,
                      bool(fields["conflict"]))
