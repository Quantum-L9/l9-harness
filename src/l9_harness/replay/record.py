from __future__ import annotations

from typing import Any

from ..domain.digests import content_id
from ..domain.provenance import utc_now


def make_record(
    run_key: str,
    baseline_digest: dict[str, Any],
    actual_digest: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    semantic = {
        "runKey": run_key,
        "baseline": baseline_digest,
        "actual": actual_digest,
        "comparison": comparison,
    }
    return {
        "schema": "l9.replay-record",
        "schemaVersion": "1.0.0",
        "replayId": content_id("replay", semantic),
        **semantic,
        "recordedAt": utc_now(),
    }
