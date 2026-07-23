from __future__ import annotations
from pathlib import Path

def ensure_layout(root: Path) -> dict[str, Path]:
    result = {k: root / k for k in ('observations', 'supporting', 'assurance')}
    for p in result.values():
        p.mkdir(parents=True, exist_ok=True)
    return result
