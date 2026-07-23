from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / "src/l9_harness"

def test_no_patch_application_or_github_publication_symbols():
    source = "\n".join(path.read_text() for path in ROOT.rglob("*.py"))
    for prohibited in ("git apply", "apply_patch", "create_check_run", "merge_pull_request"):
        assert prohibited not in source
