from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..domain.digests import canonical_json_bytes, digest_bytes


def run_vectors(root: Path) -> dict[str, Any]:
    results = []
    for p in sorted(root.glob("*.json")):
        vector = json.loads(p.read_text())
        actual = canonical_json_bytes(vector["input"]).decode()
        ok = actual == vector["expectedCanonicalJson"]
        results.append({"path": p.name, "pass": ok, "actualDigest": digest_bytes(actual.encode())})
    return {
        "kind": "canonicalization",
        "results": results,
        "pass": bool(results) and all(x["pass"] for x in results),
    }
