from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GENERATORS = (
    "scripts/generate_bindings.py",
    "scripts/update_schema_registry.py",
    "scripts/update_fixtures.py",
    "scripts/update_filetree.py",
    "scripts/update_manifest.py",
    "scripts/generate_source_identity.py",
    "scripts/update_tracked_files.py",
)


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def clean_caches() -> None:
    for path in ROOT.rglob("*"):
        if path.is_dir() and path.name in {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }:
            shutil.rmtree(path, ignore_errors=True)


def refresh_generated() -> None:
    for generator in GENERATORS:
        run([sys.executable, "-B", generator])


def main() -> None:
    clean_caches()
    refresh_generated()
    run([sys.executable, "-B", "scripts/verify_generated.py"])
    clean_caches()
    run([sys.executable, "-B", "scripts/validate_repository.py"])
    run([sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts", "build_backend.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    clean_caches()
    run([sys.executable, "-B", "scripts/verify_generated.py"])
    clean_caches()
    run([sys.executable, "-B", "scripts/validate_repository.py"])
    clean_caches()
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    run(["uv", "build", "--offline"])
    (DIST / ".gitignore").unlink(missing_ok=True)
    run([sys.executable, "scripts/finalize_distribution.py"])


if __name__ == "__main__":
    main()
