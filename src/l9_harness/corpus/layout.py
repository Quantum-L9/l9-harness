from __future__ import annotations

from pathlib import Path


def layout(root: Path) -> dict[str, Path]:
    d = {"cache": root / "cache", "outbox": root / "outbox", "snapshots": root / "snapshots"}
    for p in d.values():
        p.mkdir(parents=True, exist_ok=True)
    return d
