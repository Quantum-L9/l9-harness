import zipfile
from pathlib import Path

import build_backend


def test_editable_wheel_uses_source_pth(tmp_path):
    name = build_backend.build_editable(str(tmp_path))
    wheel = tmp_path / name
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        pth = [item for item in names if item.endswith("_editable.pth")]
        assert len(pth) == 1
        assert archive.read(pth[0]).decode().strip() == str((Path.cwd() / "src").resolve())
        assert "l9_harness/__init__.py" not in names
