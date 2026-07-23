from pathlib import Path

import pytest

from l9_harness.planning.assurance_plan import inspect_assurance_plan, load_assurance_plan
from l9_harness.sdk.capability_manifest import load_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_development_plan_has_full_shape_without_mutation():
    plan = load_assurance_plan(
        ROOT / "fixtures/assurance/development/assurance-plan.json",
        production=True,
    )
    assert inspect_assurance_plan(plan) == {"complete": True, "missing": []}
    assert not any(key.startswith("_harness") for key in plan)


def test_sdk_development_manifest_is_not_production_authority():
    with pytest.raises(ValueError):
        load_manifest(ROOT / "fixtures/sdk/development/capability-manifest.json", production=True)
