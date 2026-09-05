from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...assurance.cli_adapter import invoke, resolve_executable
from ...assurance.commands import misplaced_harness_options
from ...assurance.versioning import authority_complete, verify_authority_executable
from ...domain.errors import ContractError
from ...domain.reason_codes import ReasonCode


def command(
    executable: str,
    args: list[str],
    cwd: Path,
    invocations: Path,
    authority_path: Path | None = None,
    production: bool = False,
) -> dict[str, Any]:
    misplaced = misplaced_harness_options(args)
    if misplaced:
        raise ContractError(
            ReasonCode.INPUT_INVALID,
            "Harness options must precede the assurance operation; "
            f"{', '.join(misplaced)} was forwarded to assurance instead. "
            "Write: l9-harness assurance "
            "--executable ... <operation> <assurance flags>.",
            details={"misplaced_options": misplaced},
        )
    # Resolved here as well as in `invoke`, so that `verify_authority_executable`
    # digests the same file the invocation runs. Two independent PATH lookups of
    # one bare name could in principle disagree; `resolve_executable` is
    # idempotent on the absolute path it returns, so `invoke` re-resolving it
    # changes nothing.
    executable = resolve_executable(executable)
    authority = None
    if authority_path:
        authority = json.loads(authority_path.read_text("utf-8"))
    if production:
        if authority is None:
            raise ValueError("Production Assurance invocation requires --authority")
        complete, missing = authority_complete(authority)
        if not complete:
            raise ValueError("Incomplete Assurance authority: " + ", ".join(missing))
        verified, detail = verify_authority_executable(executable, authority)
        if not verified:
            raise ValueError(detail)
    result = invoke(executable, args, cwd, invocations)
    if authority is not None:
        result["record"]["authorityRef"] = authority
        record_path = result["root"] / "invocation-record.json"
        record_path.write_text(
            json.dumps(result["record"], sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    return {
        "status": "pass" if result["record"]["exitCode"] in {0, 10, 20, 30} else "fail",
        "artifacts": [{"path": result["root"].as_posix()}],
        "details": result["record"],
        "authoritative": False,
    }
