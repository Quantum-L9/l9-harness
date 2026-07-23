from __future__ import annotations
from pathlib import Path
from ..domain.digests import digest_file, digest_canonical, content_id

def build_manifest(root: Path, run_key: str, assurance_input_digest: dict | None=None) -> dict:
    files = []
    for p in sorted(root.rglob('*')):
        if p.is_file():
            files.append({'path': p.relative_to(root).as_posix(), 'byteLength': p.stat().st_size, 'rawDigest': digest_file(p)})
    semantic = {'runKey': run_key, 'files': files, 'assuranceInputDigest': assurance_input_digest}
    return {'schema': 'l9.harness-run-bundle-manifest', 'schemaVersion': '1.0.0', 'bundleId': content_id('run-bundle', semantic), 'runKey': run_key, 'files': files, 'assuranceInputDigest': assurance_input_digest, 'runBundleContentDigest': digest_canonical(semantic, 'run-bundle-content'), 'archiveDigest': None}
