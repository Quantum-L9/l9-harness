from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def command(root: Path) -> dict[str, Any]:
    removed = []
    for rel in (".l9/harness/runs", "artifacts"):
        p = root / rel
        if p.exists():
            shutil.rmtree(p)
            removed.append(rel)
    return {"status": "pass", "details": {"removed": removed}}
