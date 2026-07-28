from l9_harness.domain.digests import canonical_json_bytes, content_id, digest_canonical


def test_canonical_order():
    assert canonical_json_bytes({"b": 1, "a": 2}) == b'{"a":2,"b":1}'


def test_digest_deterministic():
    assert digest_canonical({"x": 1}, "x") == digest_canonical({"x": 1}, "x")


def test_domain_separation():
    assert digest_canonical({"x": 1}, "a") != digest_canonical({"x": 1}, "b")


def test_content_id():
    assert content_id("thing", {"x": 1}).startswith("thing:sha256:")
