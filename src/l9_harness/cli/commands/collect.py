from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...observations.index import build_index


def command(subject_path: Path, observation_dir: Path, output: Path) -> dict[str, Any]:
    subject = json.loads(subject_path.read_text())["subject"]
    paths = sorted(observation_dir.glob("*.json"))
    index = build_index(paths, subject)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, sort_keys=True, indent=2))
    return {
        "status": "pass" if index["counts"]["invalid"] == 0 else "partial",
        "artifacts": [{"path": output.as_posix()}],
        "details": index["counts"],
    }
