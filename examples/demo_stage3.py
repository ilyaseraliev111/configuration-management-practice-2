"""Проверяет BFS, глубину, циклы, версии, provides и неверные данные."""
from common import RUNTIME_ERROR, run_case
from http_fixture import repository_server


def options(name, depth=3, version="1.0-r0"):
    """Формирует параметры тестового JSON-репозитория с корнем A."""
    return ["--package", "A", "--version", version, "--test-repo",
            "--repository", "examples/repos/" + name,
            "--max-depth", str(depth)]


def check_json_graphs():
    """Демонстрирует цепь, ромб, цикл, петлю и отдельную компоненту."""
    cases = [("chain.json", "C=1.0-r0 -> D=1.0-r0"),
             ("diamond.json", "C=1.0-r0 -> D=1.0-r0"),
             ("cycle.json", "C=1.0-r0 -> A=1.0-r0"),
             ("self_cycle.json", "A=1.0-r0 -> A=1.0-r0"),
             ("disconnected.json", "0\tA=1.0-r0")]
    for name, fragment in cases:
        run_case(options(name), fragment=fragment)


def check_depth_and_errors():
    """Показывает границы глубины, точную версию и ожидаемые ошибки."""
    for depth, absent in [(0, "B="), (1, "C="), (2, "D=")]:
        output = run_case(options("chain.json", depth), fragment="0\tA=")
        if absent in output:
            raise AssertionError("раскрыт узел за границей глубины")
    run_case(options("versions.json"), fragment="B=1.5-r0")
    run_case(options("versions.json", version="2.0-r0"), fragment="B=2.5-r0")
    for name in ["missing_dependency.json", "invalid_schema.json"]:
        run_case(options(name), RUNTIME_ERROR, fragment="Ошибка:")
    run_case(options("chain.json", version="9.0-r0"), RUNTIME_ERROR)


def check_http_graph():
    """Проверяет транзитивность, библиотеки so: и пропуск !конфликта."""
    with repository_server() as source:
        args = ["--package", "example-app", "--version", "1.0-r0",
                "--repository", source]
        output = run_case(args, fragment="zlib=1.3.2-r1 -> musl=1.2.5-r13")
        if "conflicting-app=" in output:
            raise AssertionError("отрицательное ограничение стало ребром")


def main():
    """Запускает все воспроизводимые демонстрации этапа 3 без интернета."""
    check_json_graphs()
    check_depth_and_errors()
    check_http_graph()
    print("Этап 3: все проверки пройдены")


if __name__ == "__main__":
    main()
