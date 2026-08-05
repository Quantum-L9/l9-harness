from __future__ import annotations

from pathlib import Path

from ..security.subprocesses import run_argv


def git_text(repo: Path, *args: str) -> str:
    cp = run_argv(["git", *args], repo, 30)
    if cp.returncode:
        raise RuntimeError(cp.stderr.decode("utf-8", "replace"))
    return cp.stdout.decode().strip()


def resolve_commit(repo: Path, selector: str = "HEAD") -> str:
    return git_text(repo, "rev-parse", "--verify", f"{selector}^{{commit}}")


def tree_digest(repo: Path, commit: str) -> str:
    return git_text(repo, "rev-parse", f"{commit}^{{tree}}")


def is_clean(repo: Path) -> bool:
    return git_text(repo, "status", "--porcelain=v1") == ""


def repository_remote(repo: Path) -> str:
    try:
        return git_text(repo, "config", "--get", "remote.origin.url")
    except RuntimeError:
        return "UNKNOWN"
