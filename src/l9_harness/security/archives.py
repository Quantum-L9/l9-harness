from __future__ import annotations

import os
import zipfile
from pathlib import Path

from ..domain.errors import SecurityError
from ..domain.reason_codes import ReasonCode
from .paths import confined, normalize_relative


def _unsafe(message: str) -> SecurityError:
    return SecurityError(str(ReasonCode.ARCHIVE_UNSAFE), message)


def safe_extract_zip(
    archive: Path,
    target: Path,
    max_bytes: int = 536_870_912,
    max_files: int = 10_000,
    max_ratio: int = 1_000,
) -> list[Path]:
    total = 0
    extracted: list[Path] = []
    names: set[str] = set()
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as handle:
        infos = handle.infolist()
        if len(infos) > max_files:
            raise _unsafe("Archive file count exceeds limit")
        for info in infos:
            raw_name = info.filename.rstrip("/")
            if not raw_name:
                continue
            name = normalize_relative(raw_name)
            normalized = name.as_posix()
            if normalized in names:
                raise _unsafe(f"Duplicate archive path: {normalized}")
            names.add(normalized)
            if info.flag_bits & 0x1:
                raise _unsafe("Encrypted archive entries are prohibited")
            total += info.file_size
            if total > max_bytes:
                raise _unsafe("Archive expanded size exceeds limit")
            if info.compress_size == 0 and info.file_size > 0:
                raise _unsafe("Archive entry has invalid compression metadata")
            if info.compress_size and info.file_size / info.compress_size > max_ratio:
                raise _unsafe("Archive compression ratio exceeds limit")
            destination = confined(target, target / name)
            mode = info.external_attr >> 16 & 0o170000
            if mode == 0o120000:
                raise _unsafe("Symlink entries are prohibited")
            for parent in destination.parents:
                if parent == target.parent:
                    break
                if parent.exists() and parent.is_symlink():
                    raise _unsafe("Extraction parent symlink is prohibited")
                if parent == target:
                    break
            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            with handle.open(info, "r") as source, destination.open("xb") as output:
                while chunk := source.read(1024 * 1024):
                    written += len(chunk)
                    if written > info.file_size or written > max_bytes:
                        raise _unsafe("Archive entry exceeded declared size")
                    output.write(chunk)
            os.chmod(destination, 0o600)
            extracted.append(destination)
    return extracted
