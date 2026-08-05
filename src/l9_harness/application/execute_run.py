from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.errors import ContractError
from ..domain.reason_codes import ReasonCode
from ..execution.workspace import IsolatedWorkspace
from ..sdk.adapter import SDKAdapter
from ..sdk.invocation import invoke
from ..subject.lock import create_subject_lock, revalidate_subject


def execute(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    repo: Path,
    run_dir: Path,
) -> list[dict[str, Any]]:
    if not plan.get("complete"):
        raise ContractError(
            str(ReasonCode.CONTRACT_UNKNOWN),
            "Incomplete plans cannot execute",
            details={"unresolved": plan.get("unresolvedRequirements", [])},
        )
    current_lock = create_subject_lock(repo)
    if current_lock["subjectIdentityDigest"] != plan["subjectLockDigest"]:
        raise ContractError(str(ReasonCode.SUBJECT_CHANGED), "Subject changed before execution")
    subject = plan.get("subject", current_lock["subject"])
    if subject != current_lock["subject"]:
        raise ContractError(
            str(ReasonCode.SUBJECT_CHANGED), "Plan subject does not match repository"
        )
    lock = {"subject": subject, "subjectIdentityDigest": plan["subjectLockDigest"]}
    sdk = SDKAdapter(manifest)
    records: list[dict[str, Any]] = []
    adapter = plan.get("execution", {}).get("adapter", "process")
    commit = subject["revision"]["commit"]
    for step in plan["steps"]:
        step_output = run_dir / step["stepId"].split(":")[-1]
        with IsolatedWorkspace(repo, commit) as workspace:
            capability = {
                **sdk.capability(step["capabilityRef"]),
                "subjectDigest": plan["subjectLockDigest"],
                "producerId": manifest.get("id", "l9-ci-sdk"),
            }
            records.append(
                invoke(step, capability, workspace, plan["planId"], step_output, adapter)
            )
        if not revalidate_subject(repo, lock):
            raise ContractError(
                str(ReasonCode.SUBJECT_CHANGED), "Source repository changed during execution"
            )
    return records
