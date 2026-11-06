"""Автоматическая демонстрация порядка загрузки и ожидаемых ошибок."""
from common import RUNTIME_ERROR, run_case
from http_fixture import repository_server


def options(name, depth=3):
    """Возвращает параметры режима загрузки от корня A."""
    return ["--package", "A", "--version", "1.0-r0", "--test-repo",
            "--repository", "examples/repos/" + name, "--max-depth",
            str(depth), "--load-order"]


def main():
    """Проверяет цепь, ромб, отдельную компоненту, версии, циклы и HTTP."""
    for name, first in [("chain.json", "1\tD=1.0-r0"),
                        ("diamond.json", "1\tD=1.0-r0"),
                        ("disconnected.json", "1\tA=1.0-r0"),
                        ("versions.json", "1\tB=1.5-r0")]:
        run_case(options(name), fragment=first)
    for name in ["cycle.json", "self_cycle.json"]:
        run_case(options(name), RUNTIME_ERROR, fragment="цикл")
    run_case(options("chain.json", 1), RUNTIME_ERROR, fragment="увеличьте")
    run_case(options("missing_dependency.json"), RUNTIME_ERROR)
    with repository_server() as source:
        run_case(["--package", "example-app", "--version", "1.0-r0",
                  "--repository", source, "--load-order"],
                 fragment="1\tmusl=1.2.5-r13")
    print("Этап 4: все проверки пройдены")


if __name__ == "__main__":
    main()
