from __future__ import annotations
import subprocess
from pathlib import Path
from ..security.subprocesses import clean_environment, run_argv

def execute(argv: list[str], cwd: Path, timeout: int, allow_env: list[str] | None=None) -> subprocess.CompletedProcess[bytes]:
    return run_argv(argv, cwd, timeout, clean_environment(allow_env or []))
