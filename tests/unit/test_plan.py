from l9_harness.domain.digests import digest_bytes
from l9_harness.planning.capability_resolution import resolve_plan


def test_resolves_six_checks_from_complete_contract():
    checks = [
        "l9.repository-metadata",
        "l9.transport-packet",
        "l9.sdk-validation",
        "l9.lint",
        "l9.tests",
        "l9.mandatory-findings",
    ]
    build_digest = digest_bytes(b"sdk")
    subject = {
        "kind": "git-revision",
        "repository": {"host": "github.com", "owner": "Quantum-L9", "name": "fixture"},
        "revision": {"commit": "a" * 40, "treeDigest": digest_bytes(b"tree")},
    }
    lock = {"subjectIdentityDigest": digest_bytes(b"subject"), "subject": subject}
    execution = {
        "adapter": "process",
        "isolation": "workspace",
        "concurrency": 1,
        "timeoutSeconds": 300,
        "environmentAllowlist": [],
        "network": "denied",
    }
    profile = {"id": "p", "version": "1.0.0", "execution": execution}
    plan_contract = {
        "schema": "l9.assurance-plan",
        "schemaVersion": "1.0.0",
        "planId": "l9.assurance-plan:sha256:" + "d" * 64,
        "subject": subject,
        "profile": {"id": "p", "version": "1.0.0", "digest": digest_bytes(b"p")},
        "policy": {"id": "policy", "version": "1.0.0", "digest": digest_bytes(b"policy")},
        "registryDigests": {
            "producers": digest_bytes(b"p"),
            "checks": digest_bytes(b"c"),
            "controls": digest_bytes(b"x"),
        },
        "waiverRules": [],
        "requirements": [
            {
                "requirementId": check,
                "controlRef": check,
                "mandatory": True,
                "producer": {
                    "id": "l9-ci-sdk",
                    "acceptedVersions": ["2.0.0"],
                    "acceptedBuildDigests": [build_digest],
                },
                "check": {"id": check, "acceptedVersions": ["1.0.0"]},
                "subjectKind": "git-revision",
                "observationSchemaRef": "l9.observation@1.0.0",
                "configurationContractRef": "l9.sdk-check-config@1.0.0",
                "cardinality": {"minimum": 1, "maximum": 1},
                "supportingArtifacts": [],
                "alternatives": [],
            }
            for check in checks
        ],
    }
    sdk = {
        "id": "l9-ci-sdk",
        "version": "2.0.0",
        "buildDigest": build_digest,
        "capabilities": [
            {
                "capabilityId": check,
                "checkId": check,
                "version": "1.0.0",
                "observationSchemaRef": "l9.observation@1.0.0",
                "configurationContractRef": "l9.sdk-check-config@1.0.0",
                "configurationDigest": digest_bytes(b"config"),
                "subjectKinds": ["git-revision"],
                "timeoutSeconds": 30,
                "network": "denied",
            }
            for check in checks
        ],
    }
    plan = resolve_plan(lock, profile, plan_contract, sdk)
    assert plan["complete"]
    assert len(plan["resolvedChecks"]) == 6
    assert plan["execution"] == execution


def test_incomplete_assurance_plan_is_not_guessed():
    lock = {"subjectIdentityDigest": digest_bytes(b"s"), "subject": {"kind": "git-revision"}}
    profile = {"id": "p", "version": "1.0.0", "execution": {"timeoutSeconds": 30}}
    plan = resolve_plan(lock, profile, {"planId": "opaque"}, {"capabilities": []})
    assert not plan["complete"]
    assert plan["resolvedChecks"] == []
    assert plan["unresolvedRequirements"]
