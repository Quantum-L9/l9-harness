from __future__ import annotations

import json
import tomllib
from pathlib import Path

from release_identity import (
    EXCLUDED_SOURCE_PATHS,
    MUTABLE_EVIDENCE_PATHS,
    file_digest,
    source_records,
    source_tree_digest,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "distribution" / "source-identity.json"
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]


def build_identity() -> dict[str, object]:
    records = source_records(ROOT)
    return {
        "schema": "l9.harness-source-identity",
        "schemaVersion": "2.0.0",
        "package": PROJECT["name"],
        "version": PROJECT["version"],
        "sourceRepository": "Quantum-L9/l9-harness",
        "identityScope": "approved-source-graph",
        "sourceCommit": "UNKNOWN_REPOSITORY_UNAVAILABLE",
        "sourceTreeDigest": source_tree_digest(records),
        "sourceFileCount": len(records),
        "schemaRegistryDigest": file_digest(ROOT / "schemas" / "v1" / "registry.json"),
        "fixtureManifestDigest": file_digest(ROOT / "fixtures" / "manifest.json"),
        "specificationDigest": file_digest(ROOT / "SPECIFICATION.md"),
        "buildBackendDigest": file_digest(ROOT / "build_backend.py"),
        "exclusions": sorted(EXCLUDED_SOURCE_PATHS),
        "mutableEvidenceExclusions": sorted(MUTABLE_EVIDENCE_PATHS),
        "files": records,
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_identity(), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
