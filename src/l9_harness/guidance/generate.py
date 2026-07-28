from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_bytes
from .templates import CLAUDE_TEMPLATE, CURSOR_TEMPLATE


def generate(root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    outputs = {
        "CLAUDE.md": CLAUDE_TEMPLATE.replace("{{ profile.id }}", str(profile["id"])).replace(
            "{{ profile.version }}", str(profile["version"])
        ),
        ".cursor/rules/l9.mdc": CURSOR_TEMPLATE,
    }
    refs = []
    for rel, text in outputs.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        refs.append(
            {
                "path": rel,
                "byteLength": len(text.encode()),
                "rawDigest": digest_bytes(text.encode()),
                "canonicalPayloadDigest": None,
            }
        )
    return {
        "schema": "l9.guidance-manifest",
        "schemaVersion": "1.0.0",
        "authoritative": False,
        "outputs": refs,
        "sources": [profile.get("id", "UNKNOWN")],
    }
