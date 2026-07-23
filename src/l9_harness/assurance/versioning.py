from __future__ import annotations

import shutil
from pathlib import Path

from ..domain.digests import digest_file

REQUIRED_RELEASE_FIELDS = (
    "repository",
    "release",
    "commit_sha",
    "release_artifact_digest",
    "executable_build_digest",
    "schema_registry_digest",
    "profile_policy_registry_digest_set",
    "canonicalization_fixture_set_digest",
    "sbom_digest",
    "provenance_digest",
    "promotion_adr",
)


def authority_complete(authority: dict) -> tuple[bool, list[str]]:
    missing = [
        key
        for key in REQUIRED_RELEASE_FIELDS
        if not authority.get(key) or authority.get(key) == "UNKNOWN"
    ]
    return (not missing, missing)


def verify_authority_executable(executable: str, authority: dict) -> tuple[bool, str]:
    resolved = shutil.which(executable) or executable
    path = Path(resolved)
    if not path.is_file():
        return (False, f"Assurance executable not found: {executable}")
    expected = authority.get("executable_build_digest")
    if not isinstance(expected, dict):
        return (False, "Assurance executable digest is not a digest object")
    actual = digest_file(path)
    if actual != expected:
        return (False, "Assurance executable build digest mismatch")
    return (True, path.resolve().as_posix())
