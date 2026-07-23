from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from release_identity import MUTABLE_EVIDENCE_PATHS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "requirements" / "tracked-files.yaml"
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
EXCLUDED_PATHS = {OUTPUT.relative_to(ROOT).as_posix(), *MUTABLE_EVIDENCE_PATHS}
META_REF = "L9_META.yaml"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def classify(relative: str) -> str:
    if relative.startswith("tests/"):
        return "test"
    if relative.startswith("docs/") or relative.endswith(".md"):
        return "documentation"
    if relative.startswith("schemas/"):
        return "schema"
    if relative.startswith("fixtures/"):
        return "fixture"
    if relative.startswith("src/") or relative.startswith("scripts/"):
        return "implementation"
    if relative.startswith(".github/"):
        return "ci"
    if relative.startswith("distribution/"):
        return "distribution_identity"
    return "configuration"


def tracked_records(root: Path = ROOT) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        if relative in EXCLUDED_PATHS:
            continue
        records.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "role": classify(relative),
                "meta_ref": META_REF,
            }
        )
    return records


def render(records: list[dict[str, Any]]) -> str:
    lines = [
        "schema: l9.tracked-files/v1",
        "repository: Quantum-L9/l9-harness",
        "baseline: UNKNOWN_REPOSITORY_UNAVAILABLE",
        f"metadata_ref: {META_REF}",
        "metadata_inheritance: every_entry",
        "scope: immutable_and_operational_source_files",
        "excluded_mutable_evidence:",
        *[f"  - {yaml_quote(path)}" for path in sorted(MUTABLE_EVIDENCE_PATHS)],
        f"file_count: {len(records)}",
        "files:",
    ]
    for record in records:
        lines.extend(
            [
                f"  - path: {yaml_quote(str(record['path']))}",
                f"    sha256: {record['sha256']}",
                f"    bytes: {record['bytes']}",
                f"    role: {record['role']}",
                f"    meta_ref: {record['meta_ref']}",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    records = tracked_records()
    OUTPUT.write_text(render(records), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(records)} files")


if __name__ == "__main__":
    main()
