from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ..security.subprocesses import run_argv


class IsolatedWorkspace:
    def __init__(self, source: Path, commit: str):
        self.source = source.resolve()
        self.commit = commit
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="l9-harness-"))
        workspace = self.path / "repo"
        clone = run_argv(
            [
                "git",
                "clone",
                "--quiet",
                "--local",
                "--no-hardlinks",
                str(self.source),
                str(workspace),
            ],
            self.path,
            120,
        )
        if clone.returncode:
            shutil.rmtree(self.path, ignore_errors=True)
            raise RuntimeError(clone.stderr.decode("utf-8", "replace"))
        checkout = run_argv(["git", "checkout", "--quiet", "--detach", self.commit], workspace, 60)
        if checkout.returncode:
            shutil.rmtree(self.path, ignore_errors=True)
            raise RuntimeError(checkout.stderr.decode("utf-8", "replace"))
        return workspace

    def __exit__(self, *_: object) -> None:
        if self.path:
            shutil.rmtree(self.path, ignore_errors=True)
