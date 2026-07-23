from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import build_backend

ROOT = Path(__file__).resolve().parents[2]


def _verify_module():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = ROOT / "scripts" / "verify_distribution.py"
    spec = importlib.util.spec_from_file_location("verify_distribution_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_distribution_manifest_binds_repository_validation(tmp_path: Path) -> None:
    build_backend.build_wheel(str(tmp_path))
    build_backend.build_sdist(str(tmp_path))
    shutil.copyfile(
        ROOT / "docs" / "validation" / "repository-validation.json",
        tmp_path / "repository-validation.json",
    )
    result = _verify_module().verify(tmp_path)
    assert result["status"] == "PASS"
    digest = result["manifest"]["repositoryValidationDigest"]
    assert digest["algorithm"] == "sha256"
    assert len(digest["value"]) == 64
