from __future__ import annotations
from pathlib import Path
from ..domain.digests import digest_bytes
from ..security.subprocesses import run_argv

def patch_digest(repo: Path) -> dict[str, str] | None:
    cp = run_argv(['git', 'diff', '--binary', 'HEAD'], repo, 30)
    if not cp.stdout:
        return None
    return digest_bytes(cp.stdout)
