from __future__ import annotations
from pathlib import Path
from ..execution.engine import execute_step

def invoke(step: dict, capability: dict, repo: Path, run_key: str, output_dir: Path, adapter: str='process') -> dict:
    return execute_step(step, capability, repo, run_key, output_dir, adapter)
