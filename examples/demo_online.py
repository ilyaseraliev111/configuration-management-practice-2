"""Необязательная проверка настоящего Alpine URL; нужен доступ к сети."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    """Узнаёт доступную версию busybox и передаёт её явно в CLI."""
    from common import run_case
    from src.remote import load_remote

    source = "https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64"
    repository = load_remote(source)
    package = next(p for p in repository.packages.values()
                   if p.name == "busybox")
    print(f"В репозитории обнаружен {package.key}")
    run_case(["--package", package.name, "--version", package.version,
              "--repository", source])


if __name__ == "__main__":
    main()
