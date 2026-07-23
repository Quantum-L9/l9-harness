from __future__ import annotations
import json
from pathlib import Path
DEFAULT_PROFILE = {'schema': 'l9.harness-run-profile', 'schemaVersion': '1.0.0', 'id': 'l9.harness.release-zero-local', 'version': '1.0.0', 'subjectKinds': ['git-revision'], 'assuranceProfileRef': {'id': 'l9.pull-request', 'version': '1.0.0'}, 'sdk': {'version': 'UNKNOWN', 'digest': 'UNKNOWN'}, 'execution': {'adapter': 'process', 'isolation': 'workspace', 'concurrency': 1, 'timeoutSeconds': 900, 'environmentAllowlist': [], 'network': 'denied'}, 'artifacts': {'outputDirectory': 'artifacts', 'includeSupporting': True, 'maxTotalBytes': 1073741824}, 'fallback': {'enabled': False, 'explicitOptInRequired': True}, 'corpus': {'snapshotRef': None, 'mode': 'offline'}, 'replay': {'record': True, 'strict': True}}

def command(repo: Path, package_root: Path | None=None) -> dict:
    target = repo / '.l9/harness'
    target.mkdir(parents=True, exist_ok=True)
    cfg = target / 'config.yaml'
    if not cfg.exists():
        cfg.write_text(json.dumps(DEFAULT_PROFILE, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return {'status': 'pass', 'artifacts': [{'path': cfg.as_posix()}]}
