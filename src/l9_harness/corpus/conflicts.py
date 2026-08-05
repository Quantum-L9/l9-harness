from typing import Any


def detect(local: dict[str, Any], remote: dict[str, Any]) -> list[str]:
    lm = {x["path"]: x["rawDigest"] for x in local.get("files", [])}
    rm = {x["path"]: x["rawDigest"] for x in remote.get("files", [])}
    return sorted(k for k in set(lm) & set(rm) if lm[k] != rm[k])
