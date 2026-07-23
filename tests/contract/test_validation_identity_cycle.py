from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _clean_caches() -> None:
    for path in sorted(ROOT.rglob("*"), reverse=True):
        if path.is_dir() and path.name in CACHE_NAMES:
            shutil.rmtree(path, ignore_errors=True)


def test_repository_validation_is_idempotent_and_does_not_invalidate_source_identity() -> None:
    identity = ROOT / "distribution" / "source-identity.json"
    tracked = ROOT / "docs" / "requirements" / "tracked-files.yaml"
    report = ROOT / "docs" / "validation" / "repository-validation.json"
    identity_before = identity.read_bytes()
    tracked_before = tracked.read_bytes()
    _clean_caches()

    subprocess.run(
        [sys.executable, "-B", "scripts/validate_repository.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    first_report = report.read_bytes()
    subprocess.run(
        [sys.executable, "-B", "scripts/validate_repository.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert identity.read_bytes() == identity_before
    assert tracked.read_bytes() == tracked_before
    assert report.read_bytes() == first_report
