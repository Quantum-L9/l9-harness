from __future__ import annotations

from typing import Protocol


class TelemetrySink(Protocol):
    def increment(self, name: str, value: int = 1, **labels: str) -> None: ...

    def timing(self, name: str, seconds: float, **labels: str) -> None: ...
