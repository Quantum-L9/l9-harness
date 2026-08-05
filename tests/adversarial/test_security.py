import zipfile

import pytest

from l9_harness.domain.errors import SecurityError
from l9_harness.security.archives import safe_extract_zip
from l9_harness.security.subprocesses import clean_environment


def test_zip_traversal_rejected(tmp_path):
    z = tmp_path / "x.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("../escape", "x")
    with pytest.raises(SecurityError):
        safe_extract_zip(z, tmp_path / "out")


def test_secret_env_rejected(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    with pytest.raises(SecurityError):
        clean_environment(["GITHUB_TOKEN"])
