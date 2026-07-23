from __future__ import annotations

import subprocess
from pathlib import Path

from l9_harness.cli.commands.doctor import command


def test_doctor_rejects_non_git_directory(tmp_path: Path) -> None:
    result = command(tmp_path)
    assert result["status"] == "fail"
    assert result["details"]["checks"]["git_repository"] is False


def test_doctor_accepts_git_repository(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    result = command(tmp_path)
    assert result["status"] == "pass"
    assert result["details"]["checks"]["git_repository"] is True
