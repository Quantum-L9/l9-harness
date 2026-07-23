from __future__ import annotations
from pathlib import Path
from ...bundle.archive import build_deterministic_zip

def command(source: Path, output: Path) -> dict:
    return {'status': 'pass', 'artifacts': [build_deterministic_zip(source, output)]}
