from __future__ import annotations

import re

SEMVER = re.compile("^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:[-+].*)?$")


def valid_semver(value: str) -> bool:
    return bool(SEMVER.match(value))
