from __future__ import annotations

from pathlib import Path
from typing import Any

from ..observations.preserve import preserve_file


def copy_outputs(source: Path, target: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(source)
            preserved = preserve_file(path, target / relative, target)
            result.append({
                "source": relative.as_posix(),
                "target": preserved["path"],
                "rawDigest": preserved["rawDigest"],
            })
    return result
