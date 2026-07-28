from __future__ import annotations

from pathlib import Path
from typing import Any

from ...replay.executor import replay_json


def command(expected: Path, actual: Path) -> dict[str, Any]:
    c = replay_json(expected, actual)
    return {"status": "pass" if c["pass"] else "fail", "details": c}
