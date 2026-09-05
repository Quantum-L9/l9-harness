from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from ...assurance.cli_adapter import invoke
from ...assurance.commands import misplaced_harness_options
from ...assurance.versioning import authority_complete, verify_authority_executable
from ...domain.errors import ContractError
from ...domain.reason_codes import ReasonCode


def _resolve_executable(executable: str) -> str:
    """Resolve the assurance executable to a concrete path before invoking it.

    Two reasons the bare name must not be handed to the subprocess as-is.

    A bare name is resolved from PATH at exec time, so the invocation record's
    ``argvDigest`` would say ``l9-assurance`` while some other binary of that
    name actually ran. The record is meant to bind what was executed; it cannot
    do that without the resolved path.

    And an unresolvable name reached the subprocess layer as a bare
    ``FileNotFoundError``, which the CLI reports as exit 50
    ``HARNESS_INTERNAL_INVARIANT`` -- an internal-invariant breach for what is
    plainly a caller error. It is ``HARNESS_INPUT_INVALID`` and exit 40.
    """
    candidate = Path(executable)
    if candidate.is_absolute() or len(candidate.parts) > 1:
        if not candidate.is_file():
            raise ContractError(
                ReasonCode.INPUT_INVALID,
                f"Assurance executable does not exist: {executable}",
            )
        return str(candidate.resolve())
    resolved = shutil.which(executable)
    if resolved is None:
        raise ContractError(
            ReasonCode.INPUT_INVALID,
            f"Assurance executable {executable!r} is not on PATH. Pass "
            f"--executable with a path to the l9-assurance binary.",
        )
    return str(Path(resolved).resolve())


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
    executable = _resolve_executable(executable)
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
