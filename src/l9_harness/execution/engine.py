from __future__ import annotations

import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from ..domain.digests import digest_bytes, digest_canonical
from ..domain.provenance import utc_now
from .container_adapter import execute_container
from .process_adapter import execute


def execute_step(
    step: dict[str, Any],
    capability: dict[str, Any],
    repo: Path,
    run_key: str,
    output_dir: Path,
    adapter: str = "process",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    started = time.monotonic()
    argv = list(capability["argv"])
    timeout = int(step["timeoutSeconds"])
    limitations: list[str] = []
    if adapter == "process" and step.get("network") == "denied":
        limitations.append("network_not_enforced_by_process_adapter")
    try:
        if adapter == "container":
            completed = execute_container(capability["image"], argv, repo, timeout)
        else:
            completed = execute(argv, repo, timeout, capability.get("environmentAllowlist", []))
        termination = "completed"
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        termination = "timeout"
        exit_code = None
        stdout = error.stdout or b""
        stderr = error.stderr or b"execution timeout"
    stdout_path = output_dir / "stdout.log"
    stderr_path = output_dir / "stderr.log"
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    observation_refs: list[dict[str, Any]] = []
    observations_dir = output_dir / "observations"
    for pattern in capability.get("observationGlobs", []):
        for source in sorted(repo.glob(pattern)):
            if not source.is_file() or source.is_symlink():
                continue
            relative = source.relative_to(repo)
            destination = observations_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination, follow_symlinks=False)
            raw = destination.read_bytes()
            if raw != source.read_bytes():
                raise OSError(f"Observation byte preservation failed: {relative}")
            observation_refs.append(
                {
                    "path": destination.relative_to(output_dir).as_posix(),
                    "sourcePath": relative.as_posix(),
                    "rawDigest": digest_bytes(raw),
                    "canonicalPayloadDigest": None,
                }
            )
    return {
        "schema": "l9.execution-record",
        "schemaVersion": "1.0.0",
        "executionRecordId": f"exec:{uuid.uuid4()}",
        "runKey": run_key,
        "subjectDigest": capability["subjectDigest"],
        "check": {
            "id": capability["checkId"],
            "version": capability["version"],
            "producer": capability.get("producerId", "l9-ci-sdk"),
        },
        "adapter": adapter,
        "commandDigest": digest_canonical(argv, "command"),
        "configurationDigest": capability["configurationDigest"],
        "environmentDigest": digest_canonical(
            capability.get("environmentAllowlist", []), "environment"
        ),
        "startedAt": started_at,
        "completedAt": utc_now(),
        "exitCode": exit_code,
        "termination": termination,
        "stdoutRef": {
            "path": "stdout.log",
            "byteLength": len(stdout),
            "rawDigest": digest_bytes(stdout),
            "canonicalPayloadDigest": None,
        },
        "stderrRef": {
            "path": "stderr.log",
            "byteLength": len(stderr),
            "rawDigest": digest_bytes(stderr),
            "canonicalPayloadDigest": None,
        },
        "observationRefs": observation_refs,
        "supportingArtifactRefs": [],
        "resourceUsage": {
            "wallSeconds": time.monotonic() - started,
            "cpuSeconds": None,
            "peakMemoryBytes": None,
        },
        "limitations": limitations,
    }
