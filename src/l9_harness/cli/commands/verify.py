from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...bundle.verify import verify_bundle


def command(root: Path, manifest_path: Path) -> dict[str, Any]:
    errors = verify_bundle(root, json.loads(manifest_path.read_text()))
    return {"status": "pass" if not errors else "fail", "details": {"errors": errors}}
