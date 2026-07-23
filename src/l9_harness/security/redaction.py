from __future__ import annotations
import re
PATTERNS = [re.compile('(?i)(token|password|secret|api[_-]?key)\\s*[=:]\\s*[^\\s]+'), re.compile('gh[pousr]_[A-Za-z0-9_]{20,}')]

def redact(text: str) -> str:
    for p in PATTERNS:
        text = p.sub('[REDACTED]', text)
    return text
