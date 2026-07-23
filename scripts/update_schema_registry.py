from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "v1"
OUTPUT = SCHEMA_DIR / "registry.json"


def main() -> None:
    schemas = []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        document = json.loads(path.read_text("utf-8"))
        name = path.name.removesuffix(".schema.json")
        schemas.append({
            "name": name,
            "id": document["$id"],
            "path": path.relative_to(ROOT).as_posix(),
            "digest": {"algorithm": "sha256", "value": hashlib.sha256(path.read_bytes()).hexdigest()},
        })
    payload = {
        "schema": "l9.harness-schema-registry",
        "schemaVersion": "1.0.0",
        "schemas": schemas,
    }
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(schemas)} schemas")


if __name__ == "__main__":
    main()
