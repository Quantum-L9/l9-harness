import stat
import warnings
import zipfile

import pytest

from l9_harness.bundle.archive import build_deterministic_zip
from l9_harness.domain.errors import SecurityError
from l9_harness.security.archives import safe_extract_zip


def test_bundle_builder_rejects_symlink(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    target = source / "target"
    target.write_text("x")
    (source / "link").symlink_to(target)
    with pytest.raises(ValueError):
        build_deterministic_zip(source, tmp_path / "bundle.zip")


def test_extract_rejects_duplicate_paths(tmp_path):
    archive = tmp_path / "duplicate.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("a", "one")
            handle.writestr("a", "two")
    with pytest.raises(SecurityError):
        safe_extract_zip(archive, tmp_path / "out")


def test_extract_rejects_symlink_entry(tmp_path):
    archive = tmp_path / "symlink.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr(info, "target")
    with pytest.raises(SecurityError):
        safe_extract_zip(archive, tmp_path / "out")
