from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "FILETREE.md"
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


def source_paths() -> list[str]:
    return [
        path.relative_to(ROOT).as_posix()
        for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix())
        if path.is_file()
        and not path.is_symlink()
        and not any(part in EXCLUDED_DIRS for part in path.parts)
    ]


def render(paths: list[str]) -> str:
    lines = [
        "# File Tree",
        "",
        "Deterministic source-pack inventory. Built distribution artifacts are indexed by `dist/distribution-manifest.json` and are intentionally excluded here to avoid a source-to-output identity cycle.",
        "",
        f"Source-pack files: **{len(paths)}**",
        "",
    ]
    lines.extend(f"- `{path}`" for path in paths)
    return "\n".join(lines) + "\n"


def main() -> None:
    paths = source_paths()
    OUTPUT.write_text(render(paths), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(paths)} paths")


if __name__ == "__main__":
    main()
