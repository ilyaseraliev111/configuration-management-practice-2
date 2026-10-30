"""Проверяет прямые зависимости по HTTP без внешнего доступа к сети."""
from common import RUNTIME_ERROR, run_case
from http_fixture import repository_server


def options(source, name="busybox", version="1.37.0-r20"):
    """Возвращает параметры URL и точной версии пакета."""
    return ["--package", name, "--version", version, "--repository", source]


def main():
    """Показывает разные версии, пустые зависимости и ошибки источника."""
    with repository_server() as source:
        run_case(options(source), fragment="so:libc.musl-x86_64.so.1")
        run_case(options(source, version="1.36.1-r8"),
                 fragment="musl>=1.2")
        run_case(options(source, "musl", "1.2.5-r13"), fragment="(нет)")
        run_case(options(source, version="9.9-r0"), RUNTIME_ERROR,
                 fragment="не найден")
        run_case(options(source, name="absent"), RUNTIME_ERROR)
        run_case(options(source + "/missing"), RUNTIME_ERROR)
        run_case(options(source + "/APKINDEX.tar.gz"),
                 fragment="Прямые зависимости")
    with repository_server("not an APKINDEX") as source:
        run_case(options(source), RUNTIME_ERROR, fragment="APKINDEX")
    print("Этап 2: все проверки пройдены")


if __name__ == "__main__":
    main()
