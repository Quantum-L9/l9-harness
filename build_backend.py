from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import tarfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
NAME = PROJECT["name"].replace("-", "_")
VERSION = PROJECT["version"]
DIST = f"{NAME}-{VERSION}"


def _metadata() -> bytes:
    license_text = PROJECT.get("license", {}).get("text", "UNKNOWN")
    return (
        "Metadata-Version: 2.3\n"
        f"Name: {PROJECT['name']}\n"
        f"Version: {VERSION}\n"
        f"Summary: {PROJECT['description']}\n"
        f"Requires-Python: {PROJECT['requires-python']}\n"
        f"License: {license_text}\n"
    ).encode()


def _wheel_metadata() -> bytes:
    return (
        "Wheel-Version: 1.0\n"
        "Generator: l9-harness-build-backend\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode()


def _wheel_files():
    for path in sorted((ROOT / "src" / NAME).rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            yield path, path.relative_to(ROOT / "src").as_posix()
    for directory in ("schemas", "profiles", "templates", "distribution"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and not path.is_symlink():
                relative = path.relative_to(ROOT).as_posix()
                yield path, f"{NAME}/resources/{relative}"


def _hash(data: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
    return "sha256=" + encoded


def _write_zip(archive: zipfile.ZipFile, relative: str, data: bytes) -> None:
    info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100644 & 0xFFFF) << 16
    archive.writestr(info, data, compresslevel=9)


def _build_wheel(wheel_directory: str, *, editable: bool) -> str:
    output = Path(wheel_directory) / f"{NAME}-{VERSION}-py3-none-any.whl"
    dist_info = f"{DIST}.dist-info"
    records: list[tuple[str, str, str]] = []
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        if editable:
            relative = f"_{NAME}_editable.pth"
            data = (str((ROOT / "src").resolve()) + "\n").encode()
            _write_zip(archive, relative, data)
            records.append((relative, _hash(data), str(len(data))))
        else:
            for path, relative in _wheel_files():
                data = path.read_bytes()
                _write_zip(archive, relative, data)
                records.append((relative, _hash(data), str(len(data))))
        entries = {
            f"{dist_info}/METADATA": _metadata(),
            f"{dist_info}/WHEEL": _wheel_metadata(),
            f"{dist_info}/entry_points.txt": b"[console_scripts]\nl9-harness = l9_harness.cli.app:main\n",
            f"{dist_info}/top_level.txt": b"l9_harness\n",
            f"{dist_info}/licenses/LICENSE": (ROOT / "LICENSE").read_bytes(),
        }
        for relative, data in entries.items():
            _write_zip(archive, relative, data)
            records.append((relative, _hash(data), str(len(data))))
        record_relative = f"{dist_info}/RECORD"
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        for record in records:
            writer.writerow(record)
        writer.writerow((record_relative, "", ""))
        _write_zip(archive, record_relative, buffer.getvalue().encode())
    return output.name


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel(wheel_directory, editable=False)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel(wheel_directory, editable=True)


def build_sdist(sdist_directory, config_settings=None):
    output = Path(sdist_directory) / f"{NAME}-{VERSION}.tar.gz"
    prefix = f"{NAME}-{VERSION}"
    excludes = {
        ".git",
        ".venv",
        "dist",
        "build",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(ROOT.rglob("*")):
            if (
                not path.is_file()
                or path.is_symlink()
                or any(part in excludes for part in path.parts)
            ):
                continue
            relative = Path(prefix) / path.relative_to(ROOT)
            info = archive.gettarinfo(str(path), arcname=relative.as_posix())
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with path.open("rb") as handle:
                archive.addfile(info, handle)
    with output.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9
        ) as compressed:
            compressed.write(tar_buffer.getvalue())
    return output.name


def get_requires_for_build_wheel(config_settings=None):
    return []


def get_requires_for_build_editable(config_settings=None):
    return []


def get_requires_for_build_sdist(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    directory = Path(metadata_directory) / f"{DIST}.dist-info"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "METADATA").write_bytes(_metadata())
    (directory / "WHEEL").write_bytes(_wheel_metadata())
    return directory.name


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)
