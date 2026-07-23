from l9_harness.bundle.manifest import build_manifest
from l9_harness.bundle.verify import verify_bundle


def test_bundle_detects_mutation_and_unlisted_files(tmp_path):
    (tmp_path / "a").write_text("a")
    manifest = build_manifest(tmp_path, "run")
    assert verify_bundle(tmp_path, manifest) == []
    (tmp_path / "a").write_text("b")
    assert verify_bundle(tmp_path, manifest) == ["digest:a"]
    (tmp_path / "a").write_text("a")
    (tmp_path / "extra").write_text("extra")
    assert verify_bundle(tmp_path, manifest) == ["unlisted:extra"]
