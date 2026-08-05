from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Cache:
    def __init__(self, root: Path):
        self.root = root

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.root / f"{key}.json"
        return json.loads(path.read_text("utf-8")) if path.exists() else None

    def put(self, key: str, value: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / f"{key}.json").write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
