from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_profile(path: Path) -> dict[str, Any]:
    text = path.read_text("utf-8")
    try:
        result: dict[str, Any] = json.loads(text)
        return result
    except json.JSONDecodeError as e:
        raise ValueError("Profiles must use the JSON-compatible subset of YAML") from e
