from typing import Any

KNOWN_OPERATIONAL_FIELDS = {
    "executionId",
    "attempt",
    "startedAt",
    "completedAt",
    "resourceUsage",
    "logLocations",
}


def unexpected_fields(comparison: dict[str, Any]) -> list[str]:
    return [x["field"] for x in comparison.get("mismatches", []) if x["class"] == "semantic"]
