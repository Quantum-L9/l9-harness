from __future__ import annotations

from typing import Any

ASSURANCE_PLAN_SCHEMA = "l9.assurance-plan"
REQUIRED_PLAN_FIELDS = {
    "schema", "schemaVersion", "planId", "subject", "profile", "policy",
    "registryDigests", "requirements", "waiverRules",
}
REQUIRED_REQUIREMENT_FIELDS = {
    "requirementId", "controlRef", "mandatory", "producer", "check",
    "subjectKind", "observationSchemaRef", "configurationContractRef",
    "cardinality", "supportingArtifacts", "alternatives",
}


def plan_contract_complete(plan: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = sorted(REQUIRED_PLAN_FIELDS - set(plan))
    if plan.get("schema") != ASSURANCE_PLAN_SCHEMA:
        missing.append("schema:l9.assurance-plan")
    requirements = plan.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        missing.append("requirements:non-empty-array")
        requirements = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            missing.append(f"requirements[{index}]:object")
            continue
        for field in sorted(REQUIRED_REQUIREMENT_FIELDS - set(requirement)):
            missing.append(f"requirements[{index}].{field}")
        for identity in ("producer", "check"):
            value = requirement.get(identity)
            if not isinstance(value, dict):
                missing.append(f"requirements[{index}].{identity}:object")
                continue
            for field in ("id", "acceptedVersions"):
                if not value.get(field):
                    missing.append(f"requirements[{index}].{identity}.{field}")
        producer = requirement.get("producer", {})
        if not producer.get("acceptedBuildDigests"):
            missing.append(f"requirements[{index}].producer.acceptedBuildDigests")
    return (not missing, sorted(set(missing)))
