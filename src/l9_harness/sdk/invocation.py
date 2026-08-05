from __future__ import annotations

from pathlib import Path
from typing import Any

from ..execution.engine import execute_step


def invoke(
    step: dict[str, Any],
    capability: dict[str, Any],
    repo: Path,
    run_key: str,
    output_dir: Path,
    adapter: str = "process",
) -> dict[str, Any]:
    return execute_step(step, capability, repo, run_key, output_dir, adapter)
