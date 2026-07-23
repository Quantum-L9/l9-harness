from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
OUTPUT = FIXTURES / "manifest.json"
EXCLUDED = {OUTPUT.name}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    files = []
    for path in sorted(FIXTURES.rglob("*"), key=lambda item: item.relative_to(FIXTURES).as_posix()):
        if not path.is_file() or path.name in EXCLUDED or "__pycache__" in path.parts:
            continue
        files.append(
            {
                "path": path.relative_to(FIXTURES).as_posix(),
                "sha256": digest(path),
                "bytes": path.stat().st_size,
            }
        )
    payload = {
        "schema": "l9.harness-fixture-manifest/v1",
        "files": files,
        "fixtureSetDigest": hashlib.sha256(
            json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(files)} fixtures")


if __name__ == "__main__":
    main()
