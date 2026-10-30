"""Разбор APKINDEX, точной версии и архива без готовых APK-библиотек."""
import gzip
import io
from pathlib import Path
import tarfile
import unittest
from unittest.mock import patch
from src.apk_index import parse_index
from src.remote import download_index, index_url, unpack_index
from examples.http_fixture import index_archive, repository_server, tar_bytes

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class IndexTests(unittest.TestCase):
    """Ошибки формата и версии должны обнаруживаться до построения графа."""

    def test_fields_and_versions(self):
        """Поля с двоеточиями не обрезаются, версии хранятся раздельно."""
        repo = parse_index((EXAMPLES / "apk/APKINDEX").read_text())
        new = repo.exact("busybox", "1.37.0-r20")
        old = repo.exact("busybox", "1.36.1-r8")
        self.assertEqual(new.dependencies, ("so:libc.musl-x86_64.so.1",))
        self.assertEqual(old.dependencies, ("musl>=1.2",))
        self.assertEqual(repo.exact("musl", "1.2.5-r13").dependencies, ())
        self.assertIn("so:libc.musl-x86_64.so.1=1",
                      repo.exact("musl", "1.2.5-r13").provides)

    def test_invalid_records(self):
        """Проверяет пустой индекс, поля, повторы и отсутствующие P/V."""
        for text in ["", "P:A", "P:A\nV:bad", "wrong", "PP:A\nV:1",
                     "P:A\nP:B\nV:1", "P:A\nV:1\nk:bad",
                     "P:A\nV:1\nk:-1", "P:A\nV:1\n\nP:A\nV:1"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_index(text)

    def test_crlf_and_no_final_blank(self):
        """Текст из Windows и отсутствие последней пустой строки допустимы."""
        repo = parse_index("P:A\r\nV:1.0-r0\r\nD:B C")
        self.assertEqual(repo.exact("A", "1.0-r0").dependencies, ("B", "C"))

    def test_missing_version(self):
        """Несуществующая версия не заменяется другой доступной версией."""
        repo = parse_index("P:A\nV:1.0-r0")
        with self.assertRaisesRegex(ValueError, "доступно: 1.0-r0"):
            repo.exact("A", "2.0-r0")

    def test_signed_archive(self):
        """После gzip-потока подписи читается сам APKINDEX."""
        text = "P:A\nV:1.0-r0\n"
        self.assertEqual(unpack_index(index_archive(text)), text)

    def test_bad_archive(self):
        """Ошибки gzip, tar, отсутствия APKINDEX и UTF-8 понятны."""
        data = [b"not gzip", gzip.compress(b"not tar"),
                gzip.compress(tar_bytes("OTHER", b"data")),
                gzip.compress(tar_bytes("APKINDEX", b"\xff"))]
        for raw in data:
            with self.subTest(raw=raw[:10]):
                with self.assertRaises(ValueError):
                    unpack_index(raw)

    def test_archive_directory(self):
        """Каталог APKINDEX не должен считаться текстовым индексом."""
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:") as archive:
            info = tarfile.TarInfo("APKINDEX")
            info.type = tarfile.DIRTYPE
            archive.addfile(info)
        with self.assertRaisesRegex(ValueError, "должен быть файлом"):
            unpack_index(gzip.compress(buffer.getvalue()))

    def test_http_and_url(self):
        """Оба варианта URL загружают индекс; HTTP 404 даёт ошибку."""
        with repository_server() as source:
            self.assertEqual(index_url(source),
                             source + "/APKINDEX.tar.gz")
            raw = download_index(source)
            self.assertIn("P:busybox", unpack_index(raw))
            self.assertEqual(download_index(index_url(source)), raw)
            with self.assertRaisesRegex(ValueError, "загрузить"):
                download_index(source + "/missing")

    def test_network_error_and_size(self):
        """Сетевые ошибки и чрезмерный размер не дают traceback в CLI."""
        with patch("src.remote.urlopen", side_effect=TimeoutError):
            with self.assertRaisesRegex(ValueError, "загрузить"):
                download_index("https://example.org/apk")
        with repository_server() as source:
            with patch("src.remote.MAX_DOWNLOAD", 1):
                with self.assertRaisesRegex(ValueError, "лимит"):
                    download_index(source)
        with patch("src.remote.MAX_UNPACKED", 1):
            with self.assertRaisesRegex(ValueError, "лимит"):
                unpack_index(index_archive("P:A\nV:1"))
