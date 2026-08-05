from __future__ import annotations

from pathlib import Path
from typing import Any

from .producer_identity import FALLBACK_PRODUCER
from .regex_scanner import scan


def run_fallback(root: Path, subject: dict[str, Any]) -> dict[str, Any]:
    findings = scan(root)
    return {
        "schema": "l9.diagnostic-observation",
        "schemaVersion": "1.0.0",
        "producer": FALLBACK_PRODUCER,
        "subject": subject,
        "check": {"id": "l9.harness-diagnostic-fallback", "version": "1.0.0"},
        "status": "failed" if findings else "passed",
        "findings": findings,
        "limitations": ["Not admissible as Release-zero l9-ci-sdk evidence"],
    }
