from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..contracts.assurance import plan_contract_complete
from ..domain.errors import ContractError
from ..domain.reason_codes import ReasonCode


def load_assurance_plan(path: Path, *, production: bool = False) -> dict[str, Any]:
    plan: dict[str, Any] = json.loads(path.read_text("utf-8"))
    complete, missing = plan_contract_complete(plan)
    if production and not complete:
        raise ContractError(
            str(ReasonCode.ASSURANCE_PLAN_SCHEMA_UNAVAILABLE),
            "Assurance plan contract incomplete",
            details={"missing": missing},
        )
    return plan


def inspect_assurance_plan(plan: dict[str, Any]) -> dict[str, Any]:
    complete, missing = plan_contract_complete(plan)
    return {"complete": complete, "missing": missing}
