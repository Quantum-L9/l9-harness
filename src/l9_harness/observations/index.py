from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.digests import digest_bytes, digest_canonical
from .validate import validate_observation


def build_index(
    paths: list[Path],
    subject: dict[str, Any],
    execution_ref: str = "UNKNOWN",
    portable_root: Path | None = None,
) -> dict[str, Any]:
    if len(paths) > 1000:
        raise ValueError("EVIDENCE_LIMIT_EXCEEDED:observation-count")
    entries: list[dict[str, Any]] = []
    valid_count = 0
    for path in sorted(paths, key=lambda item: item.as_posix()):
        valid, reasons, document = validate_observation(path, subject)
        if valid:
            valid_count += 1
        relative = path.relative_to(portable_root).as_posix() if portable_root else path.name
        entry: dict[str, Any] = {
            "path": relative,
            "mediaType": "application/json",
            "byteLength": path.stat().st_size,
            "rawDigest": digest_bytes(path.read_bytes()),
            "canonicalPayloadDigest": None,
            "executionRecordRef": execution_ref,
            "validationReasons": reasons,
        }
        if document is not None:
            entry.update({
                "schema": document.get("schema"),
                "schemaVersion": document.get("schemaVersion"),
                "producerId": document.get("producer", {}).get("id"),
                "producerVersion": document.get("producer", {}).get("version"),
                "checkId": document.get("check", {}).get("id"),
                "checkVersion": document.get("check", {}).get("version"),
            })
        entries.append(entry)
    return {
        "schema": "l9.observation-index",
        "schemaVersion": "1.0.0",
        "subjectDigest": digest_canonical(subject, "subject-identity"),
        "entries": entries,
        "counts": {
            "total": len(paths),
            "structurallyValid": valid_count,
            "invalid": len(paths) - valid_count,
        },
    }
