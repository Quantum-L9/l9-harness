from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from ..domain.digests import digest_file


def build_deterministic_zip(source: Path, target: Path) -> dict[str, Any]:
    source = source.resolve()
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
            if path.is_symlink():
                raise ValueError(f"Symlink prohibited in bundle source: {path}")
            if not path.is_file() or path.resolve() == target:
                continue
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return {"path": target.as_posix(), "rawDigest": digest_file(target), "byteLength": target.stat().st_size}
