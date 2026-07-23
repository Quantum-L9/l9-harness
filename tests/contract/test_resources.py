from l9_harness.resources import profile_path, schema_path, source_identity_path


def test_installed_resources_available() -> None:
    assert schema_path("common.schema.json").is_file()
    assert profile_path("release-zero-local.yaml").is_file()
    assert source_identity_path().is_file()
