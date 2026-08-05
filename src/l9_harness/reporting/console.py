from __future__ import annotations

from typing import Any


def render_console(result: dict[str, Any]) -> str:
    lines = [f"{result.get('command')}: {result.get('status')} (exit {result.get('exit_code')})"]
    lines.extend(f"reason: {x}" for x in result.get("reason_codes", []))
    lines.extend(f"limitation: {x}" for x in result.get("limitations", []))
    return "\n".join(lines) + "\n"
