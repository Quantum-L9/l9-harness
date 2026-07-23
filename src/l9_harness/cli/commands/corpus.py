from __future__ import annotations
from pathlib import Path
from ...corpus.sync import pull, push, synchronize

def _count_files(path: Path) -> int:
    return sum((1 for item in path.rglob('*') if item.is_file())) if path.exists() else 0

def command(action: str, remote: Path, cache: Path, outbox: Path) -> dict:
    if action == 'pull':
        pull(remote, cache)
    elif action == 'push':
        push(outbox, remote)
    elif action == 'sync':
        synchronize(remote, cache, outbox)
    elif action != 'status':
        raise ValueError(action)
    return {'status': 'pass', 'details': {'action': action, 'remote': remote.as_posix(), 'cache': cache.as_posix(), 'outbox': outbox.as_posix(), 'remoteFiles': _count_files(remote), 'cacheFiles': _count_files(cache), 'outboxFiles': _count_files(outbox), 'automaticPromotion': False}}
