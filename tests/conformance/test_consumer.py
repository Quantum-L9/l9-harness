from l9_harness.conformance.consumer import verify_transport


def test_raw_byte_required(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.write_bytes(b'{"a":1,"b":2}')
    b.write_bytes(b'{ "b": 2, "a": 1 }')
    r = verify_transport(a, b)
    assert r["canonicalSemanticEqual"]
    assert not r["rawBytePreserved"]
    assert not r["pass"]


def test_exact_bytes_pass(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.write_bytes(b'{"a":1}')
    b.write_bytes(a.read_bytes())
    assert verify_transport(a, b)["pass"]
