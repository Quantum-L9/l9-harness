from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .limits import LIMITS

_ALLOWED_STATUSES = {"passed", "failed", "error", "skipped"}
_REQUIRED_FIELDS = (
    "schema",
    "schemaVersion",
    "observationId",
    "producer",
    "subject",
    "check",
    "execution",
    "summary",
    "findings",
    "artifacts",
)


def _depth(value: Any) -> int:
    if isinstance(value, dict):
        return 1 + max((_depth(item) for item in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((_depth(item) for item in value), default=0)
    return 0


def _oversized_string(value: Any) -> bool:
    if isinstance(value, str):
        return len(value.encode("utf-8")) > LIMITS["stringBytes"]
    if isinstance(value, dict):
        return any(_oversized_string(key) or _oversized_string(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_oversized_string(item) for item in value)
    return False


def validate_observation(
    path: Path,
    subject: dict[str, Any] | None = None,
) -> tuple[bool, list[str], dict[str, Any] | None]:
    reasons: list[str] = []
    data = path.read_bytes()
    if len(data) > LIMITS["singleBytes"]:
        return (False, ["EVIDENCE_TOO_LARGE"], None)
    try:
        document = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return (False, [f"EVIDENCE_SCHEMA_INVALID:{error}"], None)
    if not isinstance(document, dict):
        return (False, ["EVIDENCE_SCHEMA_INVALID:not-object"], None)
    for field in _REQUIRED_FIELDS:
        if field not in document:
            reasons.append(f"missing:{field}")
    if document.get("schema") != "l9.observation":
        reasons.append("schema:not-l9.observation")
    producer = document.get("producer", {})
    if not isinstance(producer, dict) or producer.get("id") != "l9-ci-sdk":
        reasons.append("producer:not-l9-ci-sdk")
    for field in ("version", "buildDigest"):
        if not isinstance(producer, dict) or not producer.get(field):
            reasons.append(f"producer:missing-{field}")
    check = document.get("check", {})
    if not isinstance(check, dict):
        reasons.append("check:not-object")
    else:
        for field in ("id", "version", "configurationDigest"):
            if not check.get(field):
                reasons.append(f"check:missing-{field}")
    execution = document.get("execution", {})
    if not isinstance(execution, dict):
        reasons.append("execution:not-object")
    else:
        if execution.get("status") not in _ALLOWED_STATUSES:
            reasons.append("execution:invalid-status")
        for field in ("runId", "attempt", "startedAt", "completedAt"):
            if field not in execution:
                reasons.append(f"execution:missing-{field}")
    if subject is not None and document.get("subject") != subject:
        reasons.append("EVIDENCE_SUBJECT_MISMATCH")
    findings = document.get("findings", [])
    if not isinstance(findings, list):
        reasons.append("findings:not-array")
        findings = []
    if len(findings) > LIMITS["findings"]:
        reasons.append("EVIDENCE_LIMIT_EXCEEDED:findings")
    artifacts = document.get("artifacts", [])
    if not isinstance(artifacts, list):
        reasons.append("artifacts:not-array")
    summary = document.get("summary", {})
    if not isinstance(summary, dict):
        reasons.append("summary:not-object")
    else:
        for field in ("findingCount", "warningCount", "errorCount", "informationalCount"):
            value = summary.get(field)
            if not isinstance(value, int) or value < 0:
                reasons.append(f"summary:invalid-{field}")
        if summary.get("findingCount") != len(findings):
            reasons.append("summary:finding-count-mismatch")
    extensions = document.get("extensions", {})
    if not isinstance(extensions, dict):
        reasons.append("extensions:not-object")
    elif len(extensions) > LIMITS["extensionNamespaces"]:
        reasons.append("EVIDENCE_LIMIT_EXCEEDED:extensions")
    elif any(not isinstance(key, str) or "." not in key for key in extensions):
        reasons.append("EVIDENCE_EXTENSION_NAMESPACE_INVALID")
    if _depth(document) > LIMITS["jsonDepth"]:
        reasons.append("EVIDENCE_LIMIT_EXCEEDED:depth")
    if _oversized_string(document):
        reasons.append("EVIDENCE_LIMIT_EXCEEDED:string")
    return (not reasons, sorted(set(reasons)), document)
