from __future__ import annotations

import shutil
import sys
from pathlib import Path

from ...security.subprocesses import run_argv


def _is_git_repository(repo: Path) -> bool:
    if shutil.which("git") is None or not repo.is_dir():
        return False
    result = run_argv(
        ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
        repo,
        10,
    )
    return result.returncode == 0 and result.stdout.decode("utf-8", "replace").strip() == "true"


def command(repo: Path) -> dict[str, object]:
    checks = {
        "python": (3, 11) <= sys.version_info[:2] < (3, 14),
        "git": shutil.which("git") is not None,
        "repository": repo.is_dir(),
        "git_repository": _is_git_repository(repo),
        "assurance": shutil.which("l9-assurance") is not None,
        "sdk": shutil.which("l9-ci-sdk") is not None,
    }
    core = ("python", "git", "repository", "git_repository")
    limitations = [f"{name} unavailable" for name in ("assurance", "sdk") if not checks[name]]
    return {
        "status": "pass" if all(checks[name] for name in core) else "fail",
        "details": {"checks": checks},
        "limitations": limitations,
    }
