from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_file


def verify_bundle(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {item["path"]: item for item in manifest.get("files", [])}
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    for path, item in expected.items():
        candidate = root / path
        if not candidate.exists():
            errors.append(f"missing:{path}")
        elif candidate.is_symlink():
            errors.append(f"symlink:{path}")
        elif digest_file(candidate) != item["rawDigest"]:
            errors.append(f"digest:{path}")
    for extra in sorted(actual - set(expected)):
        errors.append(f"unlisted:{extra}")
    return errors
