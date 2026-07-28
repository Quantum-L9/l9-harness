from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_file


def check(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors = []
    for x in manifest.get("outputs", []):
        p = root / x["path"]
        if not p.exists() or digest_file(p) != x["rawDigest"]:
            errors.append(x["path"])
    return errors
