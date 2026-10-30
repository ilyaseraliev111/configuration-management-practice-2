"""Выбор доступного пакета для зависимости, включая поля provides p."""
from collections import defaultdict
from dataclasses import dataclass
from functools import cmp_to_key
from src.dependencies import parse_dependency
from src.versions import (EQUAL, GREATER, LESS, compare_versions,
                          matches_version)

MIN_AUTO_PRIORITY = 0


@dataclass(frozen=True)
class Candidate:
    """Пакет и версия предоставляемого имени, а не обязательно версия APK."""
    package: object
    provided_version: object
    primary: bool


def accepts(candidate, dependency):
    """Применяет ограничения к версии предоставляемого имени."""
    if candidate.provided_version is None:
        return (not dependency.operator
                and candidate.package.priority > MIN_AUTO_PRIORITY)
    return matches_version(candidate.provided_version, dependency.operator,
                           dependency.version)


def compare_candidates(first, second):
    """Предпочитает прямое имя, приоритет, версию и стабильный tie-break."""
    if first.primary != second.primary:
        return GREATER if first.primary else LESS
    if first.package.priority != second.package.priority:
        return GREATER if first.package.priority > second.package.priority \
            else LESS
    version = compare_versions(first.provided_version or "0",
                               second.provided_version or "0")
    if version != EQUAL:
        return version
    if first.package.name == second.package.name:
        return compare_versions(first.package.version, second.package.version)
    return GREATER if first.package.name < second.package.name else LESS


class Resolver:
    """Индексирует реальные и предоставляемые имена один раз перед BFS."""

    def __init__(self, repository):
        """Создаёт каталог кандидатов без вызова apk или сторонних модулей."""
        self.candidates = defaultdict(list)
        for package in repository.packages.values():
            self.candidates[package.name].append(
                Candidate(package, package.version, True))
            self.add_provides(package)

    def add_provides(self, package):
        """Для p:name=version сохраняет именно предоставляемую версию."""
        for raw in package.provides:
            provided = parse_dependency(raw)
            if provided.conflict or provided.operator not in {"", "="}:
                raise ValueError(f"неверное поле provides: {raw}")
            self.candidates[provided.name].append(
                Candidate(package, provided.version or None, False))

    def resolve(self, dependency):
        """Выбирает подходящий пакет или сообщает о недостающей зависимости."""
        matching = [candidate for candidate in self.candidates[dependency.name]
                    if accepts(candidate, dependency)]
        if not matching:
            raise ValueError(f"не найдена зависимость: {dependency.raw}")
        chosen = max(matching, key=cmp_to_key(compare_candidates))
        return chosen.package
