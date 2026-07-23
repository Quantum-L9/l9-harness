from __future__ import annotations
from typing import Any

def stable_sort_dicts(items: list[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    return sorted(items, key=lambda x: tuple((str(x.get(k, '')) for k in keys)))
