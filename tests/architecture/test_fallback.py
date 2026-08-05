import pytest

from l9_harness.fallback.producer_identity import FALLBACK_PRODUCER
from l9_harness.fallback.restrictions import assert_diagnostic_only


def test_fallback_identity_distinct():
    assert FALLBACK_PRODUCER["id"] != "l9-ci-sdk" and FALLBACK_PRODUCER["authoritative"] is False


def test_fallback_cannot_complete_release_zero():
    with pytest.raises(ValueError):
        assert_diagnostic_only(False, True)
