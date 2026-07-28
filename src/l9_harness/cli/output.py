from __future__ import annotations

from typing import Any

from ..reporting.console import render_console
from ..reporting.json_output import render_json


def emit(result: dict[str, Any], json_mode: bool) -> None:
    print(render_json(result) if json_mode else render_console(result), end="")
