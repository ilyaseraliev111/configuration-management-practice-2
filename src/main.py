"""Этап 1: проверка CLI и вывод конфигурации без обращения к сети."""
from src.config import parse_config, print_config

SUCCESS = 0


def main(argv=None):
    """Выводит проверенные параметры прототипа и завершает запуск."""
    print_config(parse_config(argv))
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
