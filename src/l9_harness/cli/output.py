from __future__ import annotations
from ..reporting.json_output import render_json
from ..reporting.console import render_console

def emit(result: dict, json_mode: bool) -> None:
    print(render_json(result) if json_mode else render_console(result), end='')
