from __future__ import annotations

from pathlib import Path
from typing import Any

from ...conformance.consumer import verify_transport
from ...conformance.producer import run_producer_fixtures


def producer(fixtures: Path) -> dict[str, Any]:
    r = run_producer_fixtures(fixtures)
    return {"status": "pass" if r["pass"] else "fail", "details": r}


def consumer(source: Path, transported: Path) -> dict[str, Any]:
    r = verify_transport(source, transported)
    return {"status": "pass" if r["pass"] else "fail", "details": r}
