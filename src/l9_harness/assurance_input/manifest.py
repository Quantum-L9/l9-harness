from __future__ import annotations
from ..domain.digests import content_id, digest_canonical

def create_manifest(subject_lock: dict, profile_ref: dict, registry_digest: dict, observation_index_ref: dict, observations: list[dict], supporting: list[dict], complete: bool, limitations: list[str]) -> dict:
    semantic = {'subject': subject_lock['subject'], 'profileRef': profile_ref, 'registryDigest': registry_digest, 'observations': sorted(observations, key=lambda x: x['path']), 'supportingArtifacts': sorted(supporting, key=lambda x: x['path'])}
    aid = digest_canonical(semantic, 'assurance-input')
    return {'schema': 'l9.harness-assurance-input-manifest', 'schemaVersion': '1.0.0', 'inputSetId': content_id('assurance-input', semantic), 'subject': subject_lock['subject'], 'subjectIdentityDigest': subject_lock['subjectIdentityDigest'], 'profileRef': profile_ref, 'registryDigest': registry_digest, 'observationIndexRef': observation_index_ref, 'observations': semantic['observations'], 'supportingArtifacts': semantic['supportingArtifacts'], 'assuranceInputDigest': aid, 'completeForRequestedPlan': complete, 'limitations': limitations}
