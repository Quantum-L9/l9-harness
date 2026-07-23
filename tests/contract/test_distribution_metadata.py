from __future__ import annotations

import email.parser
import tarfile
import tomllib
import zipfile
from pathlib import Path

import build_backend

ROOT = Path(__file__).resolve().parents[2]


def test_wheel_metadata_matches_project_contract(tmp_path: Path) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
    wheel = tmp_path / build_backend.build_wheel(str(tmp_path))
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = email.parser.BytesParser().parsebytes(archive.read(metadata_name))
    assert metadata["Name"] == project["name"]
    assert metadata["Version"] == project["version"]
    assert metadata["Requires-Python"] == project["requires-python"]
    assert metadata["Summary"] == project["description"]


def test_sdist_contains_only_canonical_filetree_artifact(tmp_path: Path) -> None:
    sdist = tmp_path / build_backend.build_sdist(str(tmp_path))
    with tarfile.open(sdist, "r:gz") as archive:
        basenames = {Path(name).name for name in archive.getnames()}
    assert "FILETREE.md" in basenames
    assert "FINAL_TREE.md" not in basenames
    assert "FINAL_REPO_TREE.md" not in basenames
