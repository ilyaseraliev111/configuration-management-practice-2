"""Этап 3: транзитивный граф APK или тестового репозитория, обход BFS."""
import sys
from src.config import parse_config
from src.display import note_reserved_ascii, print_graph
from src.graph import build_graph
from src.remote import load_remote
from src.json_repository import load_test_repository

SUCCESS = 0
RUNTIME_ERROR = 1


def main(argv=None):
    """Загружает источник и строит граф точной версии до заданной глубины."""
    config = parse_config(argv)
    try:
        loader = load_test_repository if config.test_repo else load_remote
        repository = loader(config.repository)
        package = repository.exact(config.package, config.version)
        graph = build_graph(repository, package, config.max_depth)
        print_graph(graph)
        note_reserved_ascii(config)
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return RUNTIME_ERROR
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
