from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..observations.validate import validate_observation


def run_producer_fixtures(root: Path, subject: dict[str, Any] | None = None) -> dict[str, Any]:
    results = []
    for p in sorted(root.rglob("*.json")):
        try:
            raw = json.loads(p.read_text())
        except ValueError:
            # Not JSON we can read (JSONDecodeError/UnicodeDecodeError): skip
            # it via the schema check below. An OSError now propagates instead
            # of being silently reported as a non-observation file.
            raw = {}
        if raw.get("schema") != "l9.observation":
            continue
        ok, reasons, _ = validate_observation(p, subject)
        expected = "invalid" not in p.parts
        results.append(
            {
                "path": p.as_posix(),
                "expectedValid": expected,
                "actualValid": ok,
                "reasons": reasons,
                "pass": ok == expected,
            }
        )
    return {
        "schema": "l9.conformance-report",
        "schemaVersion": "1.0.0",
        "kind": "producer",
        "results": results,
        "pass": bool(results) and all(x["pass"] for x in results),
    }
