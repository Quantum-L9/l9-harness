from __future__ import annotations

from typing import Any


def status(python_bindings_enabled: bool, vectors_available: bool) -> dict[str, Any]:
    if not python_bindings_enabled:
        return {"status": "not_applicable", "reason": "Python Assurance bindings disabled"}
    if not vectors_available:
        return {"status": "blocked", "reason": "Authority-published vectors unavailable"}
    return {"status": "ready"}
