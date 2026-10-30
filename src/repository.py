"""Неизменяемые записи пакетов и выбор точной версии корня."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    """Имя, версия и поля D/p/k из APKINDEX без установки пакетов."""
    name: str
    version: str
    dependencies: tuple = ()
    provides: tuple = ()
    priority: int = 0

    @property
    def key(self):
        """Однозначный идентификатор записи, включая её версию."""
        return f"{self.name}={self.version}"


class Repository:
    """Хранит записи разных версий одного пакета раздельно."""

    def __init__(self, packages):
        """Проверяет непустой индекс и отсутствие повторных имя=версия."""
        self.packages = {}
        for package in packages:
            if package.key in self.packages:
                raise ValueError(f"повторная запись пакета: {package.key}")
            self.packages[package.key] = package
        if not self.packages:
            raise ValueError("репозиторий не содержит пакетов")

    def exact(self, name, version):
        """Выбирает ровно указанную версию; не подменяет её новой."""
        key = f"{name}={version}"
        if key not in self.packages:
            versions = sorted(p.version for p in self.packages.values()
                              if p.name == name)
            found = ", ".join(versions) or "пакет отсутствует"
            raise ValueError(f"не найден {key}; доступно: {found}")
        return self.packages[key]
