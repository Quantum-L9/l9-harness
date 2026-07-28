from pathlib import Path

from l9_harness.conformance.canonicalization import run_vectors


def test_development_vector():
    assert run_vectors(Path(__file__).resolve().parents[2] / "fixtures/assurance/canonicalization")[
        "pass"
    ]
