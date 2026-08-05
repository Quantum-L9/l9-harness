from typing import Any

from ..domain.digests import digest_canonical


def manifest_digest(manifest: dict[str, Any]) -> dict[str, Any]:
    return digest_canonical(manifest, "guidance-manifest")
