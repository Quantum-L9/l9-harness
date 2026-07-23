from __future__ import annotations
import json
from pathlib import Path
from ..domain.digests import digest_bytes, digest_canonical

def verify_transport(source: Path, transported: Path) -> dict:
    a = source.read_bytes()
    b = transported.read_bytes()
    raw_equal = digest_bytes(a) == digest_bytes(b)
    try:
        canonical_equal = digest_canonical(json.loads(a), 'assurance-decision') == digest_canonical(json.loads(b), 'assurance-decision')
    except Exception:
        canonical_equal = False
    return {'rawBytePreserved': raw_equal, 'canonicalSemanticEqual': canonical_equal, 'pass': raw_equal and canonical_equal}
