from __future__ import annotations
import json
from pathlib import Path
from ...bundle.manifest import build_manifest

def command(root: Path, run_key: str, output: Path) -> dict:
    m = build_manifest(root, run_key)
    output.write_text(json.dumps(m, sort_keys=True, indent=2))
    return {'status': 'pass', 'artifacts': [{'path': output.as_posix()}]}
