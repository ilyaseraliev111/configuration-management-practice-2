"""Этап 2: прямые зависимости точной версии пакета Alpine APK."""
import sys
from src.config import parse_config
from src.display import note_reserved_ascii, print_direct
from src.remote import load_remote

SUCCESS = 0
RUNTIME_ERROR = 1


def main(argv=None):
    """Получает метаданные по URL; ошибки источника возвращают код 1."""
    config = parse_config(argv)
    try:
        if config.test_repo:
            raise ValueError("анализ тестового JSON появится в этапе 3")
        repository = load_remote(config.repository)
        package = repository.exact(config.package, config.version)
        print_direct(package)
        note_reserved_ascii(config)
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return RUNTIME_ERROR
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
