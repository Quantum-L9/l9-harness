from __future__ import annotations
from typing import Any

def command_markdown(result: dict[str, Any]) -> str:
    return f"# {result.get('command')}\n\nStatus: `{result.get('status')}`\n\nAuthoritative: `{result.get('authoritative', False)}`\n"
