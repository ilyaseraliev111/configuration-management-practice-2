"""Сравнение версий APK собственным кодом по порядку компонентов Alpine."""
from enum import IntEnum
import re
from src.validation import validate_version

LESS = -1
EQUAL = 0
GREATER = 1
SUFFIX_NAMES = ("alpha", "beta", "pre", "rc", "", "cvs", "svn", "git",
                "hg", "p")
SUFFIX_ORDER = {name: rank for rank, name in enumerate(SUFFIX_NAMES)}
NO_SUFFIX = SUFFIX_ORDER[""]
PART = re.compile(
    r"(?P<number>^[0-9]+|\.[0-9]+)|"
    r"_(?P<suffix>alpha|beta|pre|rc|cvs|svn|git|hg|p)(?P<count>[0-9]*)|"
    r"(?P<letter>[a-z])|(?P<commit>~[0-9a-f]+)|(?P<revision>-r[0-9]+)"
)
RESULTS = {"": {LESS, EQUAL, GREATER}, "=": {EQUAL}, "<": {LESS},
           ">": {GREATER}, "<=": {LESS, EQUAL}, ">=": {GREATER, EQUAL},
           "~": {EQUAL}, "<~": {LESS, EQUAL}, ">~": {GREATER, EQUAL}}


class Kind(IntEnum):
    """Порядок типов компонентов; end сравнивается после остальных."""
    initial = 0
    number = 1
    letter = 2
    suffix = 3
    suffix_number = 4
    commit = 5
    revision = 6
    end = 7


def version_tokens(version):
    """Разбивает проверенную версию на числа, суффиксы, hash и ревизию."""
    validate_version(version)
    tokens = []
    for match in PART.finditer(version):
        fields = match.groupdict()
        if fields["number"]:
            raw = fields["number"]
            kind = Kind.number if raw.startswith(".") else Kind.initial
            value = raw.lstrip(".") if kind == Kind.number else int(raw)
            tokens.append((kind, value))
        elif fields["suffix"]:
            tokens.append((Kind.suffix, SUFFIX_ORDER[fields["suffix"]]))
            tokens.append((Kind.suffix_number, int(fields["count"] or "0")))
        elif fields["letter"]:
            tokens.append((Kind.letter, fields["letter"]))
        elif fields["commit"]:
            tokens.append((Kind.commit, fields["commit"][1:]))
        else:
            tokens.append((Kind.revision, int(fields["revision"][2:])))
    return [*tokens, (Kind.end, "")]


def compare_tokens(left, right):
    """Сравнивает значения одного типа, сохраняя правила ведущих нулей."""
    kind, first = left
    second = right[1]
    if kind == Kind.number:
        if not first.startswith("0") and not second.startswith("0"):
            first, second = int(first), int(second)
    return (first > second) - (first < second)


def ending_order(left, right, fuzzy):
    """Сравнивает различные типы, учитывая prerelease и префикс ~."""
    if fuzzy and right[0] == Kind.end:
        return EQUAL
    if left[0] == Kind.suffix and left[1] < NO_SUFFIX:
        return LESS
    if right[0] == Kind.suffix and right[1] < NO_SUFFIX:
        return GREATER
    return LESS if left[0] > right[0] else GREATER


def compare_versions(first, second, fuzzy=False):
    """Возвращает LESS/EQUAL/GREATER; рекурсия и APK-библиотеки не нужны."""
    for left, right in zip(version_tokens(first), version_tokens(second)):
        if left[0] != right[0]:
            return ending_order(left, right, fuzzy)
        result = compare_tokens(left, right)
        if result != EQUAL:
            return result
    return EQUAL


def matches_version(version, operator, required):
    """Проверяет ограничение APK: =, <, >, <=, >=, ~, <~, >~."""
    if operator not in RESULTS:
        raise ValueError(f"неподдерживаемое ограничение версии: {operator}")
    if not operator:
        return True
    result = compare_versions(version, required, "~" in operator)
    return result in RESULTS[operator]
