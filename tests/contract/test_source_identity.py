from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _module():
    path = ROOT / "scripts" / "release_identity.py"
    spec = importlib.util.spec_from_file_location("release_identity_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_identity_matches_approved_source_graph() -> None:
    module = _module()
    identity = json.loads((ROOT / "distribution" / "source-identity.json").read_text("utf-8"))
    records = module.source_records(ROOT)
    assert identity["sourceFileCount"] == len(records)
    assert identity["sourceTreeDigest"] == module.source_tree_digest(records)
    assert identity["files"] == records


def test_source_identity_exclusions_are_explicit() -> None:
    identity = json.loads((ROOT / "distribution" / "source-identity.json").read_text("utf-8"))
    assert identity["exclusions"] == [
        "distribution/source-identity.json",
        "docs/requirements/tracked-files.yaml",
        "docs/validation/repository-validation.json",
    ]
    assert identity["mutableEvidenceExclusions"] == [
        "docs/validation/repository-validation.json",
    ]
    assert identity["identityScope"] == "approved-source-graph"
