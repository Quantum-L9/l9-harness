from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.errors import ContractError
from ..domain.reason_codes import ReasonCode
from .adapters.filesystem import FilesystemCorpus
from .snapshot import snapshot


def _mapping(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["path"]: item["rawDigest"] for item in state.get("files", [])}


def _changed(base: dict[str, Any], current: dict[str, Any]) -> set[str]:
    base_map = _mapping(base)
    current_map = _mapping(current)
    return {
        path
        for path in set(base_map) | set(current_map)
        if base_map.get(path) != current_map.get(path)
    }


def pull(remote: Path, cache: Path) -> None:
    FilesystemCorpus(remote).pull(cache)


def push(outbox: Path, remote: Path) -> None:
    FilesystemCorpus(remote).push(outbox)


def synchronize(remote: Path, cache: Path, outbox: Path) -> None:
    remote_state = snapshot(remote)
    cache_state = snapshot(cache) if cache.exists() else {"files": []}
    outbox_state = snapshot(outbox) if outbox.exists() else {"files": []}
    remote_changed = _changed(cache_state, remote_state)
    local_changed = _changed(cache_state, outbox_state)
    remote_map = _mapping(remote_state)
    outbox_map = _mapping(outbox_state)
    conflicts = sorted(
        path
        for path in remote_changed & local_changed
        if remote_map.get(path) != outbox_map.get(path)
    )
    if conflicts:
        raise ContractError(
            str(ReasonCode.CORPUS_CONFLICT),
            "Corpus synchronization conflict",
            details={"paths": conflicts},
        )
    if outbox_state.get("files"):
        try:
            push(outbox, remote)
        except ValueError as error:
            raise ContractError(
                str(ReasonCode.CORPUS_CONFLICT),
                "Corpus submission conflict",
                details={"error": str(error)},
            ) from error
    pull(remote, cache)
