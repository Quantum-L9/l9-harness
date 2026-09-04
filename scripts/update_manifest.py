from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST.md"
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
# Kept identical across release_identity.py, update_filetree.py,
# update_manifest.py, and update_tracked_files.py: the four scanners must agree
# on the source graph or the manifest and the identity record drift apart.
# ".claude"/".cursor" are projected agent-tooling directories -- untracked,
# symlinked, and absent from the approved source graph.
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".claude",
    ".cursor",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def classify(relative: str) -> str:
    if relative.startswith("src/"):
        return "runtime"
    if relative.startswith("tests/"):
        return "test"
    if relative.startswith("schemas/"):
        return "schema"
    if relative.startswith("fixtures/"):
        return "fixture"
    if relative.startswith("scripts/") or relative == "build_backend.py":
        return "build_or_validation_tool"
    if relative.startswith(".github/"):
        return "ci"
    if relative.startswith("docs/") or relative.endswith(".md"):
        return "documentation"
    if relative.startswith("distribution/"):
        return "source_identity"
    return "configuration"


def records() -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        values.append((relative, classify(relative)))
    return values


def render(values: list[tuple[str, str]]) -> str:
    version = PROJECT["version"]
    lines = [
        "# Manifest",
        "",
        # Markdown list items rather than trailing-double-space hard breaks.
        # Trailing whitespace is stripped by ordinary formatters and pre-commit
        # catalogs, which put this generator in direct conflict with them: the
        # stripped file then fails verify_generated.py, and regenerating it
        # re-adds whitespace the hook removes again. A list keeps the three
        # fields on separate lines without depending on invisible characters.
        f"- Package: `{PROJECT['name']}`",
        f"- Version: `{version}`",
        "- Identity scope: approved source graph plus separately bound mutable validation evidence.",
        "",
        "The source identity excludes its own generated record, the generated tracked-file index, and the mutable repository-validation report. The finalized distribution copies that report into `dist/` and binds it through the distribution manifest.",
        "",
        f"## Source-pack inventory ({len(values)} files)",
        "",
        "| Path | Responsibility |",
        "|---|---|",
    ]
    lines.extend(f"| `{path}` | `{role}` |" for path, role in values)
    lines.extend(
        [
            "",
            "## Deterministic release outputs",
            "",
            f"- `dist/l9_harness-{version}-py3-none-any.whl`",
            f"- `dist/l9_harness-{version}.tar.gz`",
            f"- `dist/l9-harness-{version}-schema-bundle.zip`",
            f"- `dist/l9-harness-{version}-conformance-fixtures.zip`",
            "- `dist/repository-validation.json`",
            "- `dist/distribution-manifest.json`",
            "- `dist/distribution-alignment.json`",
            "- `dist/package-content-manifest.json`",
            "- `dist/SBOM.spdx.json`",
            "- `dist/provenance.json`",
            "- `dist/SHA256SUMS.txt`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    values = records()
    OUTPUT.write_text(render(values), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(values)} records")


if __name__ == "__main__":
    main()
