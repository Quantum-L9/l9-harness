import json
from pathlib import Path

from l9_harness.observations.index import build_index
from l9_harness.observations.validate import validate_observation

ROOT = Path(__file__).resolve().parents[2]


def test_valid_sdk_observation_passes_preflight():
    fixture = ROOT / "fixtures/sdk/valid/lint.json"
    subject = json.loads(fixture.read_text())["subject"]
    valid, reasons, _ = validate_observation(fixture, subject)
    assert valid
    assert reasons == []


def test_invalid_json_remains_in_index(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{")
    index = build_index([path], {"kind": "git-revision"}, portable_root=tmp_path)
    assert index["counts"] == {"total": 1, "structurallyValid": 0, "invalid": 1}
    assert index["entries"][0]["path"] == "broken.json"
    assert index["entries"][0]["canonicalPayloadDigest"] is None


def test_summary_count_mismatch_fails(tmp_path):
    fixture = json.loads((ROOT / "fixtures/sdk/valid/lint.json").read_text())
    fixture["summary"]["findingCount"] = 1
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(fixture))
    valid, reasons, _ = validate_observation(path, fixture["subject"])
    assert not valid
    assert "summary:finding-count-mismatch" in reasons
