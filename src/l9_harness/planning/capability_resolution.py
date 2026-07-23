from __future__ import annotations

from typing import Any

from ..contracts.assurance import plan_contract_complete
from ..domain.digests import content_id, digest_canonical


def _digest_equal(left: Any, right: Any) -> bool:
    return isinstance(left, dict) and isinstance(right, dict) and left == right


def _resolve_requirement(requirement: dict[str, Any], capability: dict[str, Any], sdk: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    producer = requirement["producer"]
    check = requirement["check"]
    if producer["id"] != sdk.get("id"):
        reasons.append("producer-id")
    if sdk.get("version") not in producer.get("acceptedVersions", []):
        reasons.append("producer-version")
    if sdk.get("buildDigest") not in producer.get("acceptedBuildDigests", []):
        reasons.append("producer-build-digest")
    if capability.get("checkId") != check["id"]:
        reasons.append("check-id")
    if capability.get("version") not in check.get("acceptedVersions", []):
        reasons.append("check-version")
    if capability.get("observationSchemaRef") != requirement.get("observationSchemaRef"):
        reasons.append("observation-schema")
    if capability.get("configurationContractRef") != requirement.get("configurationContractRef"):
        reasons.append("configuration-contract")
    if capability.get("subjectKinds") and requirement.get("subjectKind") not in capability["subjectKinds"]:
        reasons.append("subject-kind")
    if requirement.get("alternatives"):
        reasons.append("alternatives-unsupported")
    cardinality = requirement.get("cardinality", {})
    if cardinality.get("minimum") != 1 or cardinality.get("maximum") != 1:
        reasons.append("cardinality-unsupported")
    if requirement.get("supportingArtifacts"):
        declared = set(capability.get("supportingArtifactRefs", []))
        required = set(requirement["supportingArtifacts"])
        if not required.issubset(declared):
            reasons.append("supporting-artifacts")
    return reasons


def resolve_plan(
    subject_lock: dict[str, Any],
    profile: dict[str, Any],
    assurance_plan: dict[str, Any],
    sdk_authority: dict[str, Any],
    *,
    allow_fallback: bool = False,
) -> dict[str, Any]:
    del allow_fallback
    contract_complete, missing = plan_contract_complete(assurance_plan)
    capabilities = {
        capability["checkId"]: capability
        for capability in sdk_authority.get("capabilities", [])
        if isinstance(capability, dict) and capability.get("checkId")
    }
    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    if not contract_complete:
        for item in missing:
            unresolved.append({
                "requirementRef": "assurance-plan-contract",
                "reasonCode": "HARNESS_ASSURANCE_PLAN_SCHEMA_UNAVAILABLE",
                "detail": item,
            })
    else:
        for order, requirement in enumerate(assurance_plan["requirements"]):
            check_id = requirement["check"]["id"]
            capability = capabilities.get(check_id)
            if capability is None:
                unresolved.append({
                    "requirementRef": requirement["requirementId"],
                    "reasonCode": "HARNESS_SDK_CAPABILITY_UNRESOLVED",
                    "detail": f"No SDK capability for {check_id}",
                })
                continue
            mismatches = _resolve_requirement(requirement, capability, sdk_authority)
            if mismatches:
                unresolved.append({
                    "requirementRef": requirement["requirementId"],
                    "reasonCode": "HARNESS_SDK_CAPABILITY_UNRESOLVED",
                    "detail": ",".join(mismatches),
                })
                continue
            entry = {
                "evidenceRequirementRef": requirement["requirementId"],
                "controlRef": requirement["controlRef"],
                "check": {
                    "id": check_id,
                    "version": capability["version"],
                    "producer": sdk_authority["id"],
                },
                "capabilityRef": capability["capabilityId"],
                "required": bool(requirement["mandatory"]),
                "executionOrder": order,
                "cardinality": requirement["cardinality"],
                "observationSchemaRef": requirement["observationSchemaRef"],
                "configurationContractRef": requirement["configurationContractRef"],
            }
            resolved.append(entry)
            timeout = min(
                int(capability.get("timeoutSeconds", profile["execution"]["timeoutSeconds"])),
                int(profile["execution"]["timeoutSeconds"]),
            )
            network = capability.get("network", "denied")
            if profile["execution"]["network"] == "denied":
                network = "denied"
            step = {
                "stepId": content_id("harness-step", entry),
                "kind": "sdk_check",
                "checkRef": check_id,
                "capabilityRef": capability["capabilityId"],
                "dependsOn": [],
                "required": entry["required"],
                "timeoutSeconds": timeout,
                "outputContractRef": capability["observationSchemaRef"],
                "network": network,
            }
            steps.append(step)
    semantic = {
        "subjectLockDigest": subject_lock["subjectIdentityDigest"],
        "subject": subject_lock["subject"],
        "profile": profile,
        "assurancePlanDigest": digest_canonical(assurance_plan, "external-assurance-plan-bytes-model"),
        "sdkAuthorityDigest": digest_canonical(sdk_authority, "external-sdk-authority-model"),
        "resolvedChecks": resolved,
        "unresolvedRequirements": unresolved,
        "steps": steps,
    }
    return {
        "schema": "l9.harness-plan",
        "schemaVersion": "1.0.0",
        "planId": content_id("harness-plan", semantic),
        "subjectLockDigest": subject_lock["subjectIdentityDigest"],
        "subject": subject_lock["subject"],
        "execution": profile["execution"],
        "assurancePlanRef": {
            "id": assurance_plan.get("planId", "UNKNOWN"),
            "version": assurance_plan.get("schemaVersion", "UNKNOWN"),
            "digest": digest_canonical(assurance_plan, "external-assurance-plan-bytes-model"),
        },
        "runProfileRef": {
            "id": profile["id"],
            "version": profile["version"],
            "digest": digest_canonical(profile, "run-profile"),
        },
        "sdkAuthorityRef": {
            "id": sdk_authority.get("id", "UNKNOWN"),
            "version": sdk_authority.get("version", "UNKNOWN"),
            "buildDigest": sdk_authority.get("buildDigest"),
            "digest": digest_canonical(sdk_authority, "external-sdk-authority-model"),
        },
        "resolvedChecks": resolved,
        "unresolvedRequirements": unresolved,
        "steps": steps,
        "complete": contract_complete and not unresolved,
    }
