from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .compare import classify


def replay_json(expected: Path, actual: Path) -> dict[str, Any]:
    return classify(json.loads(expected.read_text()), json.loads(actual.read_text()))
