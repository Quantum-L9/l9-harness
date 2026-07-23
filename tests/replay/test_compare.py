from l9_harness.replay.compare import classify

def test_operational_difference_allowed():
    assert classify({'x': 1, 'startedAt': 'a'}, {'x': 1, 'startedAt': 'b'})['pass']

def test_semantic_difference_blocks():
    assert not classify({'x': 1}, {'x': 2})['pass']
