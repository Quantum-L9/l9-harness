from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DOMAIN_PREFIX = b"l9-harness-v2\x00"


def digest_bytes(data: bytes) -> dict[str, str]:
    return {"algorithm": "sha256", "value": hashlib.sha256(data).hexdigest()}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest_canonical(value: Any, domain: str) -> dict[str, str]:
    return digest_bytes(DOMAIN_PREFIX + domain.encode() + b"\x00" + canonical_json_bytes(value))


def digest_file(path: Path) -> dict[str, str]:
    return digest_bytes(path.read_bytes())


def content_id(namespace: str, value: Any) -> str:
    return f"{namespace}:sha256:{digest_canonical(value, namespace)['value']}"


def verify_digest(data: bytes, expected: dict[str, str]) -> bool:
    return expected.get("algorithm") == "sha256" and digest_bytes(data)["value"] == expected.get(
        "value"
    )
