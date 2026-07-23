import subprocess

import pytest

from l9_harness.subject.lock import create_subject_lock, revalidate_subject


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_git_subject_lock(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "a@b.c")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "x").write_text("x")
    _git(tmp_path, "add", "x")
    _git(tmp_path, "commit", "-qm", "x")
    lock = create_subject_lock(tmp_path)
    assert lock["resolution"]["worktree"]["clean"]
    assert revalidate_subject(tmp_path, lock)
    (tmp_path / "x").write_text("changed")
    assert not revalidate_subject(tmp_path, lock)


def test_dirty_worktree_cannot_be_locked(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "a@b.c")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "x").write_text("x")
    _git(tmp_path, "add", "x")
    _git(tmp_path, "commit", "-qm", "x")
    (tmp_path / "x").write_text("dirty")
    with pytest.raises(ValueError):
        create_subject_lock(tmp_path)
