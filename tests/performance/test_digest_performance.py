import time

from l9_harness.domain.digests import digest_canonical


def test_digest_1000_objects_under_one_second():
    start = time.perf_counter()
    for i in range(1000):
        digest_canonical({"i": i, "x": "a" * 100}, "perf")
    assert time.perf_counter() - start < 1.0
