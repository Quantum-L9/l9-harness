from __future__ import annotations

from pathlib import Path

SECRET_MARKERS = ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY", "ghp_", "AKIA")


def scan_for_secrets(root: Path) -> list[str]:
    findings = []
    for p in root.rglob("*"):
        if p.is_file() and p.stat().st_size < 2000000:
            try:
                text = p.read_text("utf-8")
            except UnicodeDecodeError:
                continue
            if any(m in text for m in SECRET_MARKERS):
                findings.append(p.relative_to(root).as_posix())
    return findings
