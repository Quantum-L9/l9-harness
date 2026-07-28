from __future__ import annotations

from typing import Any


class SDKAdapter:
    def __init__(self, manifest: dict[str, Any]):
        self.manifest = manifest
        self.by_id: dict[str, dict[str, Any]] = {
            c["capabilityId"]: c for c in manifest.get("capabilities", [])
        }

    def capability(self, ref: str) -> dict[str, Any]:
        return self.by_id[ref]
