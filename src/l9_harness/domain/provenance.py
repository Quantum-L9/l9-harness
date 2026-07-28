from __future__ import annotations

import platform
import sys
from datetime import UTC, datetime


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def runtime_provenance() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.system().lower(),
        "architecture": platform.machine().lower(),
    }
