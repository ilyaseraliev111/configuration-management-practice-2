"""Автоматическая демонстрация конфигурации и ошибок всех шести опций."""
from common import ARGUMENT_ERROR, run_case


def arguments():
    """Возвращает новый набор параметров без сетевого обращения."""
    return ["--package", "busybox", "--repository", "https://example.org/apk",
            "--version", "1.0-r0"]


def main():
    """Проверяет значения по умолчанию, флаги и некорректные опции."""
    run_case(arguments(), fragment="max_depth=3")
    run_case(arguments() + ["--ascii", "--max-depth", "0"],
             fragment="ascii=true")
    run_case(["--package", "A", "--version", "1.0-r0", "--test-repo",
              "--repository", "examples/repos/chain.json"],
             fragment="test_repo=true")
    for option, value in [("--package", "bad/name"), ("--version", "latest"),
                          ("--repository", "not-a-url")]:
        args = arguments()
        args[args.index(option) + 1] = value
        run_case(args, ARGUMENT_ERROR)
    for extra in [["--max-depth", "-1"], ["--max-depth", "abc"],
                  ["--ascii", "maybe"], ["--test-repo", "maybe"],
                  ["--test-repo"], ["--unknown"]]:
        run_case(arguments() + extra, ARGUMENT_ERROR)
    run_case([], ARGUMENT_ERROR)
    print("Этап 1: все проверки пройдены")


if __name__ == "__main__":
    main()
