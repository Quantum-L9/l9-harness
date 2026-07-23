def detect(local: dict, remote: dict) -> list[str]:
    lm = {x['path']: x['rawDigest'] for x in local.get('files', [])}
    rm = {x['path']: x['rawDigest'] for x in remote.get('files', [])}
    return sorted((k for k in set(lm) & set(rm) if lm[k] != rm[k]))
