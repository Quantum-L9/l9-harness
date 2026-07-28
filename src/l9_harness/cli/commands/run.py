from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...application.execute_run import execute


def command(repo: Path, plan_path: Path, sdk_manifest_path: Path, run_dir: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text("utf-8"))
    manifest = json.loads(sdk_manifest_path.read_text("utf-8"))
    records = execute(plan, manifest, repo, run_dir)
    output = run_dir / "execution-records.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    completed = all(record["termination"] == "completed" for record in records)
    limited = any(record.get("limitations") for record in records)
    status = "pass" if completed and not limited else "partial"
    return {
        "status": status,
        "artifacts": [{"path": output.as_posix()}],
        "limitations": sorted(
            {item for record in records for item in record.get("limitations", [])}
        ),
        "details": {"records": len(records)},
    }
