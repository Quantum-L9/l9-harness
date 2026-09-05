from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from ..domain.digests import digest_bytes, digest_canonical
from ..domain.errors import ContractError
from ..domain.provenance import utc_now
from ..domain.reason_codes import ReasonCode
from ..security.subprocesses import run_argv


def resolve_executable(executable: str) -> str:
    """Resolve the assurance executable to a concrete path before invoking it.

    This lives beside ``invoke`` because ``invoke`` is what writes
    ``argvDigest``, and the record is meant to bind what was executed. A bare
    name is resolved from PATH at exec time, so the digest would say
    ``l9-assurance`` while some other binary of that name actually ran -- the
    record could not bind anything. Enforcing that one layer up, in the CLI,
    left the four library entry points (``capture_plan``, ``admit``,
    ``simulate``, ``evaluate``) reaching ``invoke`` unbound.

    An unresolvable name is a caller error, not an internal one. Reaching the
    subprocess layer it arrives as a bare ``FileNotFoundError``, which the CLI
    reports as exit 50 ``HARNESS_INTERNAL_INVARIANT``; it is
    ``HARNESS_INPUT_INVALID`` and exit 40.

    Idempotent on an absolute path that exists, so a caller that resolves early
    -- the CLI does, so that authority verification and the invocation agree on
    one path rather than each running its own PATH lookup -- can pass the
    result down without a second resolution changing it.
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


def invoke(
    executable: str, args: list[str], cwd: Path, invocation_root: Path, timeout: int = 900
) -> dict[str, Any]:
    # Before the invocation directory is created: a refused invocation must
    # leave no artifact behind that looks like an attempted run.
    executable = resolve_executable(executable)
    iid = f"assurance-invocation:{uuid.uuid4()}"
    root = invocation_root / iid.split(":")[-1]
    root.mkdir(parents=True, exist_ok=True)
    start = utc_now()
    cp = run_argv([executable, *args], cwd, timeout)
    (root / "stdout").write_bytes(cp.stdout)
    (root / "stderr").write_bytes(cp.stderr)
    record = {
        "schema": "l9.assurance-invocation-record",
        "schemaVersion": "1.0.0",
        "invocationId": iid,
        "argvDigest": digest_canonical([executable, *args], "assurance-argv"),
        "startedAt": start,
        "completedAt": utc_now(),
        "exitCode": cp.returncode,
        "stdoutDigest": digest_bytes(cp.stdout),
        "stderrDigest": digest_bytes(cp.stderr),
        "authoritative": False,
    }
    (root / "invocation-record.json").write_text(
        json.dumps(record, sort_keys=True, indent=2), encoding="utf-8"
    )
    return {"record": record, "root": root, "stdout": cp.stdout, "stderr": cp.stderr}
