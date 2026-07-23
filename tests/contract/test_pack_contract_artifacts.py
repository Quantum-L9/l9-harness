from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_recursive_leverage_pack_artifacts_are_present_without_duplicate_tree_files() -> None:
    required = {
        "README.md",
        "MANIFEST.md",
        "FILETREE.md",
        "VALIDATION.md",
        "UNKNOWN_REGISTER.md",
        "PROVENANCE_MAP.yaml",
        "CHANGE_SUMMARY.md",
        "REGRESSION_GUARD.md",
        "TRACEABILITY_MAP.yaml",
        "DECISION_LOG.md",
        "docs/requirements/SINGLE_INGRESS_CONTRACT.yaml",
    }
    assert not [path for path in sorted(required) if not (ROOT / path).is_file()]
    assert not (ROOT / "FINAL_TREE.md").exists()
    assert not (ROOT / "FINAL_REPO_TREE.md").exists()
