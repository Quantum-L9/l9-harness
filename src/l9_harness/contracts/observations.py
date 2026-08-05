from __future__ import annotations

from typing import Any

RELEASE_ZERO_CHECKS = (
    "l9.repository-metadata",
    "l9.transport-packet",
    "l9.sdk-validation",
    "l9.lint",
    "l9.tests",
    "l9.mandatory-findings",
)


def observation_identity(doc: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(doc["producer"]["id"]),
        str(doc["producer"]["version"]),
        str(doc["check"]["id"]),
        str(doc["check"]["version"]),
    )
