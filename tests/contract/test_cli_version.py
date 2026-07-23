from __future__ import annotations

import pytest

from l9_harness.cli.app import parser
from l9_harness.domain.models import VERSION


def test_cli_version_matches_runtime_contract(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        parser().parse_args(["--version"])
    assert raised.value.code == 0
    assert capsys.readouterr().out.strip() == VERSION
