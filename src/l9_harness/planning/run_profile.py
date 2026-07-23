from __future__ import annotations
import json
from pathlib import Path

def load_profile(path: Path) -> dict:
    text = path.read_text('utf-8')
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError('Profiles must use the JSON-compatible subset of YAML') from e
