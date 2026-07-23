from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from ..domain.digests import digest_bytes, digest_canonical
from ..domain.errors import ContractError
from ..domain.models import VERSION
from ..domain.provenance import utc_now
from ..domain.reason_codes import ReasonCode
from .git import is_clean, repository_remote, resolve_commit, tree_digest
from .repository_state import patch_digest


def _parse_remote(remote: str) -> tuple[str, str, str]:
    value = remote.removesuffix(".git")
    if value.startswith("git@") and ":" in value:
        host_part, path = value.split(":", 1)
        host = host_part.split("@", 1)[1]
        parts = path.strip("/").split("/")
    elif "://" in value:
        parsed = urlparse(value)
        host = parsed.hostname or "unknown"
        parts = parsed.path.strip("/").split("/")
    else:
        host = "unknown"
        parts = value.strip("/").split("/")
    owner = parts[-2] if len(parts) >= 2 else "unknown"
    name = parts[-1] if parts else "unknown"
    return (host.lower(), owner, name)


def create_subject_lock(
    repo: Path,
    selector: str = "HEAD",
    build_digest: dict[str, str] | None = None,
    *,
    require_clean: bool = True,
) -> dict:
    commit = resolve_commit(repo, selector)
    clean = is_clean(repo)
    if require_clean and not clean:
        raise ContractError(
            str(ReasonCode.SUBJECT_DIRTY),
            "Git revision subjects require a clean worktree",
            details={"patchDigest": patch_digest(repo)},
        )
    host, owner, name = _parse_remote(repository_remote(repo))
    tree_id = tree_digest(repo, commit)
    subject = {
        "kind": "git-revision",
        "repository": {"host": host, "owner": owner, "name": name},
        "revision": {"commit": commit, "treeDigest": digest_bytes(tree_id.encode("ascii"))},
    }
    identity = digest_canonical(subject, "subject-identity")
    return {
        "schema": "l9.subject-lock",
        "schemaVersion": "1.0.0",
        "subject": subject,
        "subjectIdentityDigest": identity,
        "resolution": {
            "resolvedFrom": {
                "selector": selector,
                "selectorType": "commit" if selector == commit else "branch",
            },
            "worktree": {"clean": clean, "patchDigest": patch_digest(repo)},
            "resolvedAt": utc_now(),
            "resolver": {
                "id": "l9-harness",
                "version": VERSION,
                "buildDigest": build_digest or digest_bytes(VERSION.encode("ascii")),
            },
        },
    }


def revalidate_subject(repo: Path, lock: dict) -> bool:
    expected = lock["subject"]["revision"]
    if not is_clean(repo):
        return False
    current_commit = resolve_commit(repo, "HEAD")
    if current_commit != expected["commit"]:
        return False
    current_tree = digest_bytes(tree_digest(repo, current_commit).encode("ascii"))
    return current_tree == expected.get("treeDigest")
