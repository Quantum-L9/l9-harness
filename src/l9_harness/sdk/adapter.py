from __future__ import annotations

class SDKAdapter:

    def __init__(self, manifest: dict):
        self.manifest = manifest
        self.by_id = {c['capabilityId']: c for c in manifest.get('capabilities', [])}

    def capability(self, ref: str) -> dict:
        return self.by_id[ref]
