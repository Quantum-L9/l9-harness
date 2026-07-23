from pathlib import Path

from l9_harness.assurance.versioning import authority_complete, verify_authority_executable
from l9_harness.domain.digests import digest_file


def test_authority_requires_immutable_release_fields(tmp_path):
    executable = tmp_path / "assurance"
    executable.write_text("binary")
    authority = {
        "repository": "Quantum-L9/l9-assurance",
        "release": "2.0.0",
        "commit_sha": "a" * 40,
        "release_artifact_digest": {"algorithm": "sha256", "value": "1" * 64},
        "executable_build_digest": digest_file(executable),
        "schema_registry_digest": {"algorithm": "sha256", "value": "2" * 64},
        "profile_policy_registry_digest_set": {"algorithm": "sha256", "value": "3" * 64},
        "canonicalization_fixture_set_digest": {"algorithm": "sha256", "value": "4" * 64},
        "sbom_digest": {"algorithm": "sha256", "value": "5" * 64},
        "provenance_digest": {"algorithm": "sha256", "value": "6" * 64},
        "promotion_adr": "ADR-001",
    }
    assert authority_complete(authority) == (True, [])
    assert verify_authority_executable(str(executable), authority)[0]
    executable.write_text("changed")
    assert not verify_authority_executable(str(executable), authority)[0]
