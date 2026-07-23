from __future__ import annotations

def assert_diagnostic_only(authoritative: bool, complete_release_zero: bool) -> None:
    if authoritative or complete_release_zero:
        raise ValueError('Fallback output is diagnostic-only and cannot satisfy Release-zero')
