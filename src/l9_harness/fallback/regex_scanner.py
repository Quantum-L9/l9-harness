from __future__ import annotations

import re
from pathlib import Path
from typing import Any

RULES = {"possible-secret": re.compile("(?i)(password|secret|api[_-]?key)\\s*[=:]")}


def scan(root: Path) -> list[dict[str, Any]]:
    findings = []
    for p in root.rglob("*"):
        if not p.is_file() or any(x in p.parts for x in {".git", ".venv", "node_modules"}):
            continue
        try:
            text = p.read_text("utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for rule, pat in RULES.items():
            for m in pat.finditer(text):
                findings.append(
                    {
                        "ruleId": rule,
                        "message": f"{rule} at {p.relative_to(root)}",
                        "location": {
                            "path": p.relative_to(root).as_posix(),
                            "lineStart": text.count("\n", 0, m.start()) + 1,
                        },
                    }
                )
    return findings
