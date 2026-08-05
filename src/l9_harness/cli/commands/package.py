from __future__ import annotations

from pathlib import Path
from typing import Any

from ...bundle.archive import build_deterministic_zip


def command(source: Path, output: Path) -> dict[str, Any]:
    return {"status": "pass", "artifacts": [build_deterministic_zip(source, output)]}
