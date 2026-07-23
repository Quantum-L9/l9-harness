from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
MUTABLE_EVIDENCE_PATHS = {
    "docs/validation/repository-validation.json",
}
EXCLUDED_SOURCE_PATHS = {
    "distribution/source-identity.json",
    "docs/requirements/tracked-files.yaml",
    *MUTABLE_EVIDENCE_PATHS,
}


def raw_digest(data: bytes) -> dict[str, str]:
    return {"algorithm": "sha256", "value": hashlib.sha256(data).hexdigest()}


def file_digest(path: Path) -> dict[str, str]:
    return raw_digest(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def source_files(root: Path) -> list[Path]:
    records: list[Path] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink():
            raise RuntimeError(f"Symlink prohibited in source identity: {path}")
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        if relative in EXCLUDED_SOURCE_PATHS:
            continue
        records.append(path)
    return records


def source_records(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "byteLength": path.stat().st_size,
            "rawDigest": file_digest(path),
        }
        for path in source_files(root)
    ]


def source_tree_digest(records: Iterable[dict[str, Any]]) -> dict[str, str]:
    return raw_digest(canonical_bytes(list(records)))



def deterministic_zip(source: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(
            source.rglob("*"),
            key=lambda item: item.relative_to(source).as_posix(),
        ):
            if path.is_symlink():
                raise RuntimeError(f"Symlink prohibited in release bundle: {path}")
            if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)

def wheel_record_errors(wheel_path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(wheel_path) as archive:
        record_names = [name for name in archive.namelist() if name.endswith(".dist-info/RECORD")]
        if len(record_names) != 1:
            return [f"wheel RECORD count is {len(record_names)}"]
        rows = csv.reader(io.StringIO(archive.read(record_names[0]).decode("utf-8")))
        for relative, digest, size in rows:
            if relative == record_names[0]:
                continue
            if relative not in archive.namelist():
                errors.append(f"RECORD path missing: {relative}")
                continue
            data = archive.read(relative)
            if size and int(size) != len(data):
                errors.append(f"RECORD size mismatch: {relative}")
            if digest:
                algorithm, encoded = digest.split("=", 1)
                if algorithm != "sha256":
                    errors.append(f"RECORD algorithm unsupported: {relative}")
                    continue
                actual = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
                if actual != encoded:
                    errors.append(f"RECORD digest mismatch: {relative}")
    return errors


def safe_extract_sdist(archive_path: Path, target: Path) -> Path:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        roots = {Path(member.name).parts[0] for member in members if Path(member.name).parts}
        if len(roots) != 1:
            raise RuntimeError("sdist must contain one top-level directory")
        for member in members:
            candidate = (target / member.name).resolve()
            if target.resolve() not in candidate.parents and candidate != target.resolve():
                raise RuntimeError(f"sdist traversal entry: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"sdist link entry prohibited: {member.name}")
        archive.extractall(target, filter="data")
    return target / next(iter(roots))
