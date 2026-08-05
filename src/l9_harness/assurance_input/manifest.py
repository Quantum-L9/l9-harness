from __future__ import annotations

from typing import Any

from ..domain.digests import content_id, digest_canonical


def create_manifest(
    subject_lock: dict[str, Any],
    profile_ref: dict[str, Any],
    registry_digest: dict[str, Any],
    observation_index_ref: dict[str, Any],
    observations: list[dict[str, Any]],
    supporting: list[dict[str, Any]],
    complete: bool,
    limitations: list[str],
) -> dict[str, Any]:
    semantic = {
        "subject": subject_lock["subject"],
        "profileRef": profile_ref,
        "registryDigest": registry_digest,
        "observations": sorted(observations, key=lambda x: x["path"]),
        "supportingArtifacts": sorted(supporting, key=lambda x: x["path"]),
    }
    aid = digest_canonical(semantic, "assurance-input")
    return {
        "schema": "l9.harness-assurance-input-manifest",
        "schemaVersion": "1.0.0",
        "inputSetId": content_id("assurance-input", semantic),
        "subject": subject_lock["subject"],
        "subjectIdentityDigest": subject_lock["subjectIdentityDigest"],
        "profileRef": profile_ref,
        "registryDigest": registry_digest,
        "observationIndexRef": observation_index_ref,
        "observations": semantic["observations"],
        "supportingArtifacts": semantic["supportingArtifacts"],
        "assuranceInputDigest": aid,
        "completeForRequestedPlan": complete,
        "limitations": limitations,
    }
