from __future__ import annotations

from .errors import ContractError
from .reason_codes import ReasonCode


def require(condition: bool, reason: ReasonCode, message: str) -> None:
    if not condition:
        raise ContractError(str(reason), message)


def prohibit_authoritative_harness(value: bool) -> None:
    require(
        not value,
        ReasonCode.INTERNAL_INVARIANT,
        "Harness publication authority must always be false",
    )
