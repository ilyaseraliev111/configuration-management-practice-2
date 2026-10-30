"""Локальный HTTP-репозиторий APKINDEX для воспроизводимых демонстраций."""
from contextlib import contextmanager
from functools import partial
import gzip
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
from pathlib import Path
import tarfile
import tempfile
from threading import Thread

FIXTURE = Path(__file__).resolve().parent / "apk" / "APKINDEX"
EPHEMERAL_PORT = 0


class QuietHandler(SimpleHTTPRequestHandler):
    """Раздаёт только временную папку и не печатает журнал HTTP-запросов."""

    def log_message(self, format_string, *args):
        """Отключает служебные сообщения тестового HTTP-сервера."""


def tar_bytes(name, data):
    """Создаёт tar в памяти, без архивов в отслеживаемых файлах Git."""
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    return stream.getvalue()


def index_archive(text):
    """Имитирует два gzip-потока подписанного индекса Alpine v2."""
    signature = gzip.compress(tar_bytes(".SIGN.TEST", b"fixture"))
    index = gzip.compress(tar_bytes("APKINDEX", text.encode("utf-8")))
    return signature + index


@contextmanager
def repository_server(text=None):
    """Публикует временный APKINDEX по loopback; не требует интернета."""
    if text is None:
        text = FIXTURE.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "APKINDEX.tar.gz").write_bytes(index_archive(text))
        handler = partial(QuietHandler, directory=directory)
        server = ThreadingHTTPServer(("127.0.0.1", EPHEMERAL_PORT), handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            worker.join()
            server.server_close()
