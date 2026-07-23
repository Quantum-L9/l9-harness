from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "src" / "l9_harness" / "contracts" / "generated" / "schema_inventory.py",
    ROOT / "src" / "l9_harness" / "contracts" / "generated" / "models.py",
    ROOT / "schemas" / "v1" / "registry.json",
    ROOT / "fixtures" / "manifest.json",
    ROOT / "FILETREE.md",
    ROOT / "MANIFEST.md",
    ROOT / "docs" / "requirements" / "tracked-files.yaml",
    ROOT / "distribution" / "source-identity.json",
)
GENERATORS = (
    ROOT / "scripts" / "generate_bindings.py",
    ROOT / "scripts" / "update_schema_registry.py",
    ROOT / "scripts" / "update_fixtures.py",
    ROOT / "scripts" / "update_filetree.py",
    ROOT / "scripts" / "update_manifest.py",
    ROOT / "scripts" / "generate_source_identity.py",
    ROOT / "scripts" / "update_tracked_files.py",
)


def main() -> None:
    before = {path: path.read_bytes() if path.exists() else None for path in TARGETS}
    for generator in GENERATORS:
        subprocess.run([sys.executable, "-B", str(generator)], check=True)
    drifted = [
        path
        for path in TARGETS
        if before[path] is None or before[path] != path.read_bytes()
    ]
    if drifted:
        names = ", ".join(path.relative_to(ROOT).as_posix() for path in drifted)
        raise SystemExit(f"generated artifact drift: {names}")
    print(f"generated artifacts verified: {len(TARGETS)} files")


if __name__ == "__main__":
    main()
