"""Показывает Mermaid и ASCII на трёх пакетах и проверяет особые случаи."""
import argparse
from pathlib import Path
import sys

from common import run_case
from http_fixture import repository_server

ROOT = Path(__file__).resolve().parents[1]
ALPINE = "https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64"
ONLINE_PACKAGES = ("busybox", "zlib", "curl")
OFFLINE_PACKAGES = ("busybox", "zlib", "example-app")
FULL_DEPTH = 30


def show_packages(source, names):
    """Запускает анализ каждой точной версии в двух форматах."""
    sys.path.insert(0, str(ROOT))
    from src.remote import load_remote

    repository = load_remote(source)
    for name in names:
        package = next((p for p in repository.packages.values()
                        if p.name == name), None)
        if package is None:
            raise ValueError(f"пакет {name} не найден")
        options = ["--package", name, "--version", package.version,
                   "--repository", source, "--max-depth", str(FULL_DEPTH)]
        run_case(options, fragment=f'n0["{package.key}"]')
        run_case(options + ["--ascii"], fragment=package.key + "\n")


def show_cases():
    """Проверяет повторную вершину, цикл, петлю и усечение глубины."""
    for name, marker in [("diamond", "[shared]"), ("cycle", "[cycle]"),
                         ("self_cycle", "[cycle]")]:
        args = ["--package", "A", "--version", "1.0-r0", "--test-repo",
                "--repository", f"examples/repos/{name}.json"]
        run_case(args + ["--ascii"], fragment=marker)
    args = ["--package", "A", "--version", "1.0-r0", "--test-repo",
            "--repository", "examples/repos/chain.json", "--max-depth", "0"]
    output = run_case(args + ["--ascii"], fragment="A=1.0-r0\n")
    if output.splitlines() != ["A=1.0-r0"]:
        raise AssertionError("раскрыт узел за пределом глубины")


def main():
    """По умолчанию запускает воспроизводимую проверку без интернета."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true")
    if parser.parse_args().online:
        show_packages(ALPINE, ONLINE_PACKAGES)
    else:
        with repository_server() as source:
            show_packages(source, OFFLINE_PACKAGES)
        show_cases()
    print("Этап 5: все проверки пройдены")


if __name__ == "__main__":
    main()
