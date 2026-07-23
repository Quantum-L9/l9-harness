from __future__ import annotations
from pathlib import Path
from typing import Any
from .cli_adapter import invoke

def simulate(executable: str, profile: str, policy: Path, evidence: Path, cwd: Path, invocations: Path) -> dict[str, Any]:
    result = invoke(executable, ['simulate', '--profile', profile, '--policy', str(policy), '--evidence', str(evidence)], cwd, invocations)
    result['record']['authoritative'] = False
    return result
