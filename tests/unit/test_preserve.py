from l9_harness.observations.preserve import preserve_file


def test_preserves_exact_bytes(tmp_path):
    src = tmp_path / "a"
    dst = tmp_path / "b"
    src.write_bytes(b'{ "b": 1, "a": 2 }\n')
    ref = preserve_file(src, dst)
    assert dst.read_bytes() == src.read_bytes()
    assert ref["rawDigest"]["algorithm"] == "sha256"
