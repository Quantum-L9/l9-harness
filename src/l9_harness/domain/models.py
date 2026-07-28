from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

VERSION = "2.0.4"


@dataclass(frozen=True)
class DigestRef:
    algorithm: str
    value: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class CommandResult:
    command: str
    status: str
    exit_code: int
    reason_codes: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    authoritative: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "l9.harness-command-result",
            "schemaVersion": "1.0.0",
            **asdict(self),
        }
