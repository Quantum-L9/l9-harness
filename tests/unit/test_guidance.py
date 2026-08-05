from l9_harness.guidance.generate import generate


def test_guidance_is_non_authoritative(tmp_path):
    m = generate(tmp_path, {"id": "x", "version": "1.0.0"})
    assert m["authoritative"] is False
    assert (tmp_path / "CLAUDE.md").exists()
