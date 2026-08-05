from __future__ import annotations

import zipfile
from pathlib import Path

import build_backend

ROOT = Path(__file__).resolve().parents[2]


def test_built_wheel_embeds_exact_source_identity(tmp_path: Path) -> None:
    wheel = tmp_path / build_backend.build_wheel(str(tmp_path))
    with zipfile.ZipFile(wheel) as archive:
        assert (
            archive.read("l9_harness/resources/distribution/source-identity.json")
            == (ROOT / "distribution" / "source-identity.json").read_bytes()
        )


def test_built_wheel_matches_runtime_sources(tmp_path: Path) -> None:
    wheel = tmp_path / build_backend.build_wheel(str(tmp_path))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for source in sorted((ROOT / "src" / "l9_harness").rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            relative = source.relative_to(ROOT / "src").as_posix()
            assert relative in names
            assert archive.read(relative) == source.read_bytes()
