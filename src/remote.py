"""Получение APKINDEX по HTTP(S), чтение gzip/tar только в памяти."""
import gzip
import io
import tarfile
from urllib.error import URLError
from urllib.request import Request, urlopen
from src.apk_index import parse_index
from src.validation import validate_url

NETWORK_TIMEOUT = 20
MAX_DOWNLOAD = 16 * 1024 * 1024
MAX_UNPACKED = 96 * 1024 * 1024
INDEX_NAME = "APKINDEX"
INDEX_ARCHIVE = "APKINDEX.tar.gz"


def index_url(source):
    """Принимает каталог репозитория или полный URL APKINDEX.tar.gz."""
    validate_url(source)
    if source.endswith(INDEX_ARCHIVE):
        return source
    return source.rstrip("/") + "/" + INDEX_ARCHIVE


def download_index(source):
    """Загружает ограниченный объём данных с тайм-аутом и ошибкой сети."""
    request = Request(index_url(source),
                      headers={"User-Agent": "apk-dependency-practice/1"})
    try:
        with urlopen(request, timeout=NETWORK_TIMEOUT) as response:
            data = response.read(MAX_DOWNLOAD + 1)
    except (URLError, OSError) as error:
        raise ValueError(f"не удалось загрузить APKINDEX: {error}") from error
    if len(data) > MAX_DOWNLOAD:
        raise ValueError("APKINDEX.tar.gz превышает лимит загрузки")
    return data


def unpack_index(data):
    """Читает и подписанный многопоточный gzip; файлы не извлекает на диск."""
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            unpacked = stream.read(MAX_UNPACKED + 1)
        if len(unpacked) > MAX_UNPACKED:
            raise ValueError("распакованный индекс превышает лимит")
        with tarfile.open(fileobj=io.BytesIO(unpacked), mode="r:",
                          ignore_zeros=True) as archive:
            member = archive.getmember(INDEX_NAME)
            if not member.isfile():
                raise ValueError("элемент APKINDEX должен быть файлом")
            with archive.extractfile(member) as stream:
                return stream.read(MAX_UNPACKED + 1).decode("utf-8")
    except (OSError, EOFError, tarfile.TarError, KeyError,
            UnicodeError) as error:
        message = "неверный архив APKINDEX.tar.gz или его текст"
        raise ValueError(message) from error


def load_remote(source):
    """Загружает один индекс репозитория и строит каталог записей пакетов."""
    return parse_index(unpack_index(download_index(source)))
