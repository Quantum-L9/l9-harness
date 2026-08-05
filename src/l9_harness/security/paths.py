from __future__ import annotations

from pathlib import Path, PurePosixPath

from ..domain.errors import SecurityError
from ..domain.reason_codes import ReasonCode


def normalize_relative(path: str) -> str:
    if "\x00" in path or "\\" in path or (len(path) >= 2 and path[1] == ":"):
        raise SecurityError(str(ReasonCode.PATH_UNSAFE), f"Unsafe path: {path!r}")
    p = PurePosixPath(path)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise SecurityError(str(ReasonCode.PATH_UNSAFE), f"Unsafe relative path: {path!r}")
    return p.as_posix()


def confined(root: Path, candidate: Path) -> Path:
    r = root.resolve()
    c = candidate.resolve()
    if c != r and r not in c.parents:
        raise SecurityError(str(ReasonCode.PATH_UNSAFE), f"Path escapes root: {candidate}")
    return c
