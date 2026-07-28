from __future__ import annotations

from pathlib import Path
from typing import Any

from ..observations.preserve import preserve_file
from .layout import ensure_layout


def export_files(
    observations: list[Path], supporting: list[Path], root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    layout = ensure_layout(root)
    observation_refs = [
        preserve_file(path, layout["observations"] / path.name, root) for path in observations
    ]
    supporting_refs = [
        preserve_file(path, layout["supporting"] / path.name, root) for path in supporting
    ]
    return (observation_refs, supporting_refs)
