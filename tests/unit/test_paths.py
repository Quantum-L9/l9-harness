import pytest
from l9_harness.security.paths import normalize_relative

@pytest.mark.parametrize('p', ['/x', '../x', 'a/../b', 'C:/x', 'a\\b'])
def test_rejects_unsafe(p):
    with pytest.raises(Exception):
        normalize_relative(p)

def test_accepts_portable():
    assert normalize_relative('a/b.json') == 'a/b.json'
