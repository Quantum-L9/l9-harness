from pathlib import Path


def fixture_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())
