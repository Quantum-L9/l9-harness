from __future__ import annotations

from pathlib import Path
from typing import Any

from ...guidance.generate import generate
from ...planning.run_profile import load_profile


def command(root: Path, profile: Path) -> dict[str, Any]:
    m = generate(root, load_profile(profile))
    return {"status": "pass", "artifacts": m["outputs"], "details": m}
