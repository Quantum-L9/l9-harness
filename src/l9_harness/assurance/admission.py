from __future__ import annotations

from pathlib import Path
from typing import Any

from .cli_adapter import invoke


def admit(
    executable: str, subject: Path, observations: Path, output: Path, cwd: Path, invocations: Path
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    return invoke(
        executable,
        [
            "evidence",
            "admit",
            "--subject",
            str(subject),
            "--input",
            str(observations),
            "--output",
            str(output),
        ],
        cwd,
        invocations,
    )
