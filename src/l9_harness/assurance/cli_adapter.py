from __future__ import annotations
import json, uuid
from pathlib import Path
from ..domain.digests import digest_bytes, digest_canonical
from ..domain.provenance import utc_now
from ..security.subprocesses import run_argv

def invoke(executable: str, args: list[str], cwd: Path, invocation_root: Path, timeout: int=900) -> dict:
    iid = f'assurance-invocation:{uuid.uuid4()}'
    root = invocation_root / iid.split(':')[-1]
    root.mkdir(parents=True, exist_ok=True)
    start = utc_now()
    cp = run_argv([executable, *args], cwd, timeout)
    (root / 'stdout').write_bytes(cp.stdout)
    (root / 'stderr').write_bytes(cp.stderr)
    record = {'schema': 'l9.assurance-invocation-record', 'schemaVersion': '1.0.0', 'invocationId': iid, 'argvDigest': digest_canonical([executable, *args], 'assurance-argv'), 'startedAt': start, 'completedAt': utc_now(), 'exitCode': cp.returncode, 'stdoutDigest': digest_bytes(cp.stdout), 'stderrDigest': digest_bytes(cp.stderr), 'authoritative': False}
    (root / 'invocation-record.json').write_text(json.dumps(record, sort_keys=True, indent=2), encoding='utf-8')
    return {'record': record, 'root': root, 'stdout': cp.stdout, 'stderr': cp.stderr}
