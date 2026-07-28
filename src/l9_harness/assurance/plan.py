from __future__ import annotations

from pathlib import Path
from typing import Any

from .cli_adapter import invoke


def capture_plan(
    executable: str, subject: Path, profile: str, output: Path, cwd: Path, invocations: Path
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    return invoke(
        executable,
        ["plan", "--profile", profile, "--subject", str(subject), "--output", str(output)],
        cwd,
        invocations,
    )
