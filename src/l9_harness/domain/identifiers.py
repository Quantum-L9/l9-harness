from __future__ import annotations
from .digests import content_id

def derive_id(namespace: str, semantic_payload: object) -> str:
    return content_id(namespace, semantic_payload)
