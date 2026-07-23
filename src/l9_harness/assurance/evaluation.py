from __future__ import annotations
from pathlib import Path
from typing import Any
from .cli_adapter import invoke

def evaluate(executable: str, subject: Path, profile: str, policy: str, accepted: Path, evaluation_time: str, output: Path, cwd: Path, invocations: Path) -> dict[str, Any]:
    if accepted.name != 'accepted' or not accepted.is_dir():
        raise ValueError('Evaluation requires the exact admission/accepted directory')
    output.mkdir(parents=True, exist_ok=True)
    return invoke(executable, ['evaluate', '--subject', str(subject), '--profile', profile, '--policy', policy, '--evidence', str(accepted), '--evaluation-time', evaluation_time, '--output', str(output)], cwd, invocations)
