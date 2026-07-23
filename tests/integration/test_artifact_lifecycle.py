from l9_harness.assurance_input.export import export_files
from l9_harness.assurance_input.layout import ensure_layout

def test_export_layout_and_bytes(tmp_path):
    src = tmp_path / 'source.json'
    src.write_bytes(b'{"x":1}\n')
    root = tmp_path / 'artifacts'
    obs, _ = export_files([src], [], root)
    assert (root / 'observations/source.json').read_bytes() == src.read_bytes()
    assert obs[0]['rawDigest']
