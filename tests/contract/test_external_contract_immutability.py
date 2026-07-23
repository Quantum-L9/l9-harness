import copy
import json
from pathlib import Path

from l9_harness.planning.assurance_plan import load_assurance_plan
from l9_harness.sdk.capability_manifest import load_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_loaders_do_not_mutate_external_documents():
    plan_path = ROOT / "fixtures/assurance/development/assurance-plan.json"
    sdk_path = ROOT / "fixtures/sdk/development/capability-manifest.json"
    expected_plan = json.loads(plan_path.read_text())
    expected_sdk = json.loads(sdk_path.read_text())
    plan = load_assurance_plan(plan_path)
    sdk = load_manifest(sdk_path)
    assert plan == expected_plan
    assert sdk == expected_sdk
    assert plan is not expected_plan
    assert sdk is not expected_sdk
    assert copy.deepcopy(plan) == expected_plan
