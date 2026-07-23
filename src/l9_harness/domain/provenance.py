from __future__ import annotations
import platform, sys
from datetime import datetime, timezone

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def runtime_provenance() -> dict[str, str]:
    return {'python': sys.version.split()[0], 'platform': platform.system().lower(), 'architecture': platform.machine().lower()}
