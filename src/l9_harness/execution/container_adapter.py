from __future__ import annotations

import subprocess
from pathlib import Path

from .process_adapter import execute


def execute_container(
    image: str, argv: list[str], repo: Path, timeout: int
) -> subprocess.CompletedProcess[bytes]:
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "256",
        "--memory",
        "1g",
        "--cpus",
        "2",
        "-v",
        f"{repo.resolve()}:/workspace:rw",
        "-w",
        "/workspace",
        image,
        *argv,
    ]
    return execute(command, repo, timeout)
