import itertools

from l9_harness.domain.digests import digest_canonical


def test_mapping_order_invariant():
    items = [("a", 1), ("b", 2), ("c", 3)]
    digests = {digest_canonical(dict(p), "x")["value"] for p in itertools.permutations(items)}
    assert len(digests) == 1
