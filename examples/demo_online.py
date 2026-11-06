"""Необязательная проверка настоящего Alpine URL; нужен доступ к сети."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    """Узнаёт доступную версию busybox и передаёт её явно в CLI."""
    from common import run_case
    from src.remote import load_remote

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--load-order", action="store_true")
    args = parser.parse_args()
    source = "https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64"
    repository = load_remote(source)
    package = next(p for p in repository.packages.values()
                   if p.name == "busybox")
    print(f"В репозитории обнаружен {package.key}")
    options = ["--package", package.name, "--version", package.version,
               "--repository", source]
    if args.load_order:
        options.append("--load-order")
    run_case(options)


if __name__ == "__main__":
    main()
