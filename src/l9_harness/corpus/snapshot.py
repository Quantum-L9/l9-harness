from __future__ import annotations
from pathlib import Path
from ..domain.digests import digest_file, digest_canonical, content_id

def snapshot(root: Path) -> dict:
    files = [{'path': p.relative_to(root).as_posix(), 'rawDigest': digest_file(p)} for p in sorted(root.rglob('*')) if p.is_file()]
    return {'schema': 'l9.corpus-snapshot', 'schemaVersion': '1.0.0', 'snapshotId': content_id('corpus-snapshot', files), 'files': files, 'digest': digest_canonical(files, 'corpus-snapshot')}
