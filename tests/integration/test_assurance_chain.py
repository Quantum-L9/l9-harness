from pathlib import Path
import pytest
from l9_harness.assurance.evaluation import evaluate

def test_evaluation_requires_admission_accepted_directory(tmp_path):
    wrong = tmp_path / "evidence"
    wrong.mkdir()
    with pytest.raises(ValueError):
        evaluate("missing", tmp_path / "subject.json", "p", "policy", wrong, "2026-07-22T00:00:00Z", tmp_path / "out", tmp_path, tmp_path / "invocations")
