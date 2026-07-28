from pathlib import Path

from l9_harness.conformance.producer import run_producer_fixtures


def test_sdk_fixtures():
    root = Path(__file__).resolve().parents[2] / "fixtures/sdk"
    r = run_producer_fixtures(root)
    assert r["pass"]
