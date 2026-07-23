from l9_harness.bundle.archive import build_deterministic_zip

def test_zip_deterministic(tmp_path):
    root = tmp_path / 'r'
    root.mkdir()
    (root / 'b').write_text('b')
    (root / 'a').write_text('a')
    x = build_deterministic_zip(root, tmp_path / 'x.zip')
    y = build_deterministic_zip(root, tmp_path / 'y.zip')
    assert x['rawDigest'] == y['rawDigest']
