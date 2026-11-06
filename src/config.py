"""Настройки CLI; с этапа 4 добавлен режим порядка загрузки."""
import argparse
from dataclasses import asdict, dataclass
from src.validation import validate_name, validate_source, validate_version

DEFAULT_DEPTH = 3
ROOT_DEPTH = 0


@dataclass(frozen=True)
class Config:
    """Параметры одного запуска анализатора зависимостей."""
    package: str
    repository: str
    test_repo: bool
    version: str
    ascii: bool
    max_depth: int
    load_order: bool = False


def depth_value(value):
    """Принимает целую неотрицательную глубину; корень имеет глубину 0."""
    try:
        number = int(value)
    except ValueError as error:
        message = "глубина должна быть целой"
        raise argparse.ArgumentTypeError(message) from error
    if number < ROOT_DEPTH:
        raise argparse.ArgumentTypeError("глубина должна быть неотрицательной")
    return number


def build_parser():
    """Описывает обязательные параметры и логические флаги варианта 29."""
    parser = argparse.ArgumentParser(
        description="Зависимости Alpine APK, вариант 29", allow_abbrev=False
    )
    parser.add_argument("--package", required=True, help="Имя пакета")
    parser.add_argument("--repository", required=True,
                        help="URL репозитория или путь к тестовому JSON")
    parser.add_argument("--test-repo", action="store_true",
                        help="Использовать тестовый JSON; анализ с этапа 3")
    parser.add_argument("--version", required=True,
                        help="Точная версия корневого пакета, например 1.0-r0")
    parser.add_argument("--ascii", action="store_true",
                        help="Параметр ASCII-дерева; вывод будет на этапе 5")
    parser.add_argument("--max-depth", type=depth_value, default=DEFAULT_DEPTH,
                        help="Максимальная глубина BFS; по умолчанию 3")
    parser.add_argument("--load-order", action="store_true",
                        help="Показать порядок загрузки зависимостей (этап 4)")
    return parser


def parse_config(argv=None):
    """Разбирает опции, проверяет согласованность и выдаёт ошибки argparse."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_name(args.package, args.test_repo)
        validate_version(args.version)
        validate_source(args.repository, args.test_repo)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return Config(**vars(args))


def print_config(config):
    """Печатает настройки как ключ=значение для проверки конфигурации."""
    for key, value in asdict(config).items():
        shown = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={shown}")
