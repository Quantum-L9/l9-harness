from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import content_id, digest_canonical, digest_file


def snapshot(root: Path) -> dict[str, Any]:
    files = [
        {"path": p.relative_to(root).as_posix(), "rawDigest": digest_file(p)}
        for p in sorted(root.rglob("*"))
        if p.is_file()
    ]
    return {
        "schema": "l9.corpus-snapshot",
        "schemaVersion": "1.0.0",
        "snapshotId": content_id("corpus-snapshot", files),
        "files": files,
        "digest": digest_canonical(files, "corpus-snapshot"),
    }
