from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_bytes


def preserve_file(source: Path, target: Path, portable_root: Path | None = None) -> dict[str, Any]:
    if source.is_symlink():
        raise ValueError(f"Symlink source prohibited: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    target.write_bytes(raw)
    if target.read_bytes() != raw:
        raise OSError("Byte preservation failed")
    path = target.relative_to(portable_root).as_posix() if portable_root else target.name
    return {
        "path": path,
        "mediaType": "application/json" if target.suffix == ".json" else "application/octet-stream",
        "byteLength": len(raw),
        "rawDigest": digest_bytes(raw),
        "canonicalPayloadDigest": None,
    }
