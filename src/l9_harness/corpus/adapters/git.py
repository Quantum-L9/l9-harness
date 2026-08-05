from __future__ import annotations

import shutil
from pathlib import Path

from ...security.subprocesses import run_argv
from .filesystem import FilesystemCorpus


class GitCorpus:
    def __init__(self, remote: str, ref: str, expected_commit: str | None = None):
        self.remote = remote
        self.ref = ref
        self.expected_commit = expected_commit

    def pull(self, target: Path) -> str:
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        result = run_argv(
            ["git", "clone", "--no-checkout", self.remote, str(target)], target.parent, 600
        )
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", "replace"))
        result = run_argv(["git", "checkout", "--detach", self.ref], target, 120)
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", "replace"))
        commit = run_argv(["git", "rev-parse", "HEAD"], target, 30).stdout.decode().strip()
        if self.expected_commit and commit != self.expected_commit:
            raise RuntimeError(f"Corpus commit mismatch: {commit}")
        return commit

    def push(self, outbox: Path, checkout: Path, *, message: str, allow_push: bool = False) -> str:
        if not allow_push:
            raise RuntimeError("Git corpus push requires explicit allow_push=True")
        FilesystemCorpus(checkout).push(outbox)
        run_argv(["git", "add", "--all"], checkout, 60)
        result = run_argv(["git", "commit", "-m", message], checkout, 60)
        if result.returncode not in {0, 1}:
            raise RuntimeError(result.stderr.decode("utf-8", "replace"))
        result = run_argv(["git", "push", "origin", f"HEAD:{self.ref}"], checkout, 600)
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", "replace"))
        return run_argv(["git", "rev-parse", "HEAD"], checkout, 30).stdout.decode().strip()
