from __future__ import annotations


class HarnessError(Exception):
    """Base error with stable machine reason code."""

    def __init__(self, reason_code: str, message: str, *, details: dict[str, object] | None = None):
        super().__init__(message)
        self.reason_code = reason_code
        self.message = message
        self.details = details or {}


class ContractError(HarnessError, ValueError):
    pass


class SecurityError(HarnessError):
    pass


class ExecutionError(HarnessError):
    pass
