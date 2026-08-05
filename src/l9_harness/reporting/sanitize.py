from __future__ import annotations

import html

from ..security.redaction import redact


def sanitize_text(text: str) -> str:
    return html.escape(redact(text), quote=True)
