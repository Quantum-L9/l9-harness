from l9_harness.guidance.generate import generate


def test_guidance_is_deterministic(tmp_path):
    profile = {"id": "p", "version": "1.0.0"}
    first = generate(tmp_path, profile)
    second = generate(tmp_path, profile)
    assert first == second
