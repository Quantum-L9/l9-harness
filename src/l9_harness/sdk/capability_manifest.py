from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..contracts.sdk import validate_sdk_authority
from ..domain.errors import ContractError
from ..domain.reason_codes import ReasonCode


def load_manifest(path: Path, *, production: bool = False) -> dict[str, Any]:
    document = json.loads(path.read_text("utf-8"))
    missing = validate_sdk_authority(document)
    if production and missing:
        raise ContractError(
            str(ReasonCode.SDK_AUTHORITY_UNPINNED),
            "SDK authority incomplete",
            details={"missing": missing},
        )
    return document


def inspect_manifest(document: dict[str, Any]) -> dict[str, Any]:
    missing = validate_sdk_authority(document)
    return {"complete": not missing, "missing": missing}
