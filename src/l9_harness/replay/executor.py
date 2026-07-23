from __future__ import annotations
import json
from pathlib import Path
from .compare import classify

def replay_json(expected: Path, actual: Path) -> dict:
    return classify(json.loads(expected.read_text()), json.loads(actual.read_text()))
