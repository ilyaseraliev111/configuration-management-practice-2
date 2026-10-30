"""Проверяет три этапа, не переключая рабочую ветку пользователя."""
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STAGES = [("stage1-config", "demo_stage1.py"),
          ("stage2-fetch", "demo_stage2.py"), ("stage3-bfs", "demo_stage3.py")]


def unpack_snapshot(raw, destination):
    """Копирует обычные файлы собственного git archive в временную папку."""
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for member in archive:
            name = Path(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("неверный путь в Git-снимке")
            target = destination / name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
            else:
                raise ValueError("Git-снимок содержит не обычный файл")


def run_stage(branch, demo):
    """Запускает пример и тесты нужного коммита без изменения рабочей копии."""
    print(f"\n=== {branch} ===", flush=True)
    archive = subprocess.run(["git", "archive", "--format=tar", branch],
                             cwd=ROOT, capture_output=True, check=True)
    with tempfile.TemporaryDirectory(prefix="apk-stage-") as directory:
        temporary = Path(directory)
        unpack_snapshot(archive.stdout, temporary)
        env = {**os.environ, "PYTHONUTF8": "1"}
        subprocess.run([sys.executable, "examples/" + demo], cwd=temporary,
                       env=env, check=True)
        subprocess.run([sys.executable, "-m", "unittest", "discover",
                        "-s", "tests", "-v"], cwd=temporary, env=env,
                       check=True)


def main():
    """Требует Git и ветки трёх этапов; код 1 означает неуспешную проверку."""
    try:
        if not shutil.which("git"):
            raise ValueError("для общего прогона нужен Git в PATH")
        for branch, demo in STAGES:
            run_stage(branch, demo)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Общий прогон остановлен: {error}", file=sys.stderr)
        return 1
    print("ВСЕ ТРИ ЭТАПА: проверки пройдены")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
