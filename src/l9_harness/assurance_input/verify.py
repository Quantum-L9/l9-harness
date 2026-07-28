from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_file


def verify_manifest(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors = []
    for item in [*manifest.get("observations", []), *manifest.get("supportingArtifacts", [])]:
        p = root / item["path"]
        if not p.exists():
            errors.append(f"missing:{item['path']}")
        elif digest_file(p) != item["rawDigest"]:
            errors.append(f"digest:{item['path']}")
    return errors
