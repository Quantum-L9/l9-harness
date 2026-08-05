from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from ..domain.errors import SecurityError
from ..domain.reason_codes import ReasonCode

DENIED_ENV_PREFIXES = (
    "AWS_",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "NPM_TOKEN",
    "PYPI_TOKEN",
    "SSH_AUTH_SOCK",
)


def clean_environment(allowlist: Sequence[str] = ()) -> dict[str, str]:
    base = {
        "PATH": os.environ.get("PATH", ""),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONHASHSEED": "0",
    }
    for key in allowlist:
        if any(key.startswith(p) for p in DENIED_ENV_PREFIXES):
            raise SecurityError(
                str(ReasonCode.INPUT_INVALID), f"Secret-like environment key prohibited: {key}"
            )
        if key in os.environ:
            base[key] = os.environ[key]
    return base


def run_argv(
    argv: Sequence[str], cwd: Path, timeout: int, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[bytes]:
    if not argv or any("\x00" in a for a in argv):
        raise SecurityError(str(ReasonCode.INPUT_INVALID), "Invalid argv")
    return subprocess.run(
        list(argv),
        cwd=cwd,
        env=env or clean_environment(),
        shell=False,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
