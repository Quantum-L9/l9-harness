from __future__ import annotations

import argparse
import json
import tempfile
import tomllib
import zipfile
from pathlib import Path
from typing import Any

from release_identity import (
    EXCLUDED_DIRS,
    file_digest,
    safe_extract_sdist,
    source_records,
    source_tree_digest,
    wheel_record_errors,
)

ROOT = Path(__file__).resolve().parents[1]
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
VERSION = PROJECT["version"]
NAME = PROJECT["name"].replace("-", "_")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def _compare_bytes(left: Path, right: Path, label: str, errors: list[str]) -> None:
    if not right.is_file():
        errors.append(f"{label} missing: {right}")
    elif left.read_bytes() != right.read_bytes():
        errors.append(f"{label} byte mismatch: {left.relative_to(ROOT).as_posix()}")


def _verify_source_identity(identity: dict[str, Any], errors: list[str]) -> None:
    records = source_records(ROOT)
    if identity.get("version") != VERSION:
        errors.append("source identity version mismatch")
    if identity.get("sourceFileCount") != len(records):
        errors.append("source identity file count mismatch")
    if identity.get("sourceTreeDigest") != source_tree_digest(records):
        errors.append("source identity tree digest mismatch")
    expected = {item["path"]: item for item in records}
    actual = {item["path"]: item for item in identity.get("files", [])}
    if actual != expected:
        errors.append("source identity file records mismatch")


def _verify_wheel(wheel: Path, identity_bytes: bytes, errors: list[str]) -> dict[str, Any]:
    errors.extend(wheel_record_errors(wheel))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for path in sorted((ROOT / "src" / NAME).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(ROOT / "src").as_posix()
            if relative not in names:
                errors.append(f"wheel runtime file missing: {relative}")
            elif archive.read(relative) != path.read_bytes():
                errors.append(f"wheel runtime file mismatch: {relative}")
        for directory in ("schemas", "profiles", "templates"):
            for path in sorted((ROOT / directory).rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(ROOT).as_posix()
                packaged = f"{NAME}/resources/{relative}"
                if packaged not in names:
                    errors.append(f"wheel resource missing: {packaged}")
                elif archive.read(packaged) != path.read_bytes():
                    errors.append(f"wheel resource mismatch: {packaged}")
        identity_name = f"{NAME}/resources/distribution/source-identity.json"
        if identity_name not in names:
            errors.append("wheel source identity missing")
        elif archive.read(identity_name) != identity_bytes:
            errors.append("wheel source identity mismatch")
        payload = [name for name in sorted(names) if not name.endswith("/")]
    return {"fileCount": len(payload), "rawDigest": file_digest(wheel)}


def _verify_sdist(sdist: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="l9-harness-sdist-") as temporary:
        extracted = safe_extract_sdist(sdist, Path(temporary))
        for path in sorted(ROOT.rglob("*")):
            if path.is_symlink():
                errors.append(f"source symlink prohibited: {path.relative_to(ROOT).as_posix()}")
                continue
            if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            relative = path.relative_to(ROOT)
            _compare_bytes(path, extracted / relative, "sdist", errors)
        extra = [
            path.relative_to(extracted).as_posix()
            for path in extracted.rglob("*")
            if path.is_file() and not (ROOT / path.relative_to(extracted)).is_file()
        ]
        if extra:
            errors.append(f"sdist extra files: {sorted(extra)}")
    return {"rawDigest": file_digest(sdist)}


def verify(dist: Path) -> dict[str, Any]:
    identity_path = ROOT / "distribution" / "source-identity.json"
    identity = _load(identity_path)
    identity_bytes = identity_path.read_bytes()
    errors: list[str] = []
    _verify_source_identity(identity, errors)
    wheel = dist / f"{NAME}-{VERSION}-py3-none-any.whl"
    sdist = dist / f"{NAME}-{VERSION}.tar.gz"
    wheel_result = _verify_wheel(wheel, identity_bytes, errors)
    sdist_result = _verify_sdist(sdist, errors)
    validation_path = dist / "repository-validation.json"
    if not validation_path.is_file():
        errors.append("repository validation evidence missing from distribution")
        validation_digest = {"algorithm": "sha256", "value": "0" * 64}
    else:
        validation_digest = file_digest(validation_path)
    artifact_paths = [
        path
        for path in sorted(dist.iterdir())
        if path.is_file()
        and path.name not in {"distribution-manifest.json", "distribution-alignment.json", "SHA256SUMS.txt"}
    ]
    manifest = {
        "schema": "l9.harness-distribution-manifest",
        "schemaVersion": "2.0.0",
        "package": PROJECT["name"],
        "version": VERSION,
        "sourceIdentityDigest": file_digest(identity_path),
        "sourceTreeDigest": identity["sourceTreeDigest"],
        "repositoryValidationDigest": validation_digest,
        "wheel": wheel_result,
        "sdist": sdist_result,
        "artifacts": [
            {
                "name": path.name,
                "byteLength": path.stat().st_size,
                "rawDigest": file_digest(path),
            }
            for path in artifact_paths
        ],
    }
    return {
        "schema": "l9.harness-distribution-alignment/v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "manifest": manifest,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = verify(args.dist)
    if args.write:
        (args.dist / "distribution-manifest.json").write_text(
            json.dumps(result["manifest"], sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (args.dist / "distribution-alignment.json").write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
