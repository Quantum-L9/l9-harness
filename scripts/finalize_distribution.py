from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from release_identity import deterministic_zip, file_digest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
VERSION = PROJECT["version"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    (DIST / ".gitignore").unlink(missing_ok=True)
    wheel = DIST / f"l9_harness-{VERSION}-py3-none-any.whl"
    sdist = DIST / f"l9_harness-{VERSION}.tar.gz"
    if not wheel.is_file() or not sdist.is_file():
        raise SystemExit("wheel and sdist must exist before distribution finalization")

    deterministic_zip(ROOT / "schemas", DIST / f"l9-harness-{VERSION}-schema-bundle.zip")
    deterministic_zip(
        ROOT / "fixtures",
        DIST / f"l9-harness-{VERSION}-conformance-fixtures.zip",
    )
    help_text = subprocess.run(
        [sys.executable, "-m", "l9_harness", "--help"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    (DIST / "CLI_HELP.txt").write_text(help_text, encoding="utf-8")

    validation_source = ROOT / "docs" / "validation" / "repository-validation.json"
    validation_copy = DIST / "repository-validation.json"
    if not validation_source.is_file():
        raise SystemExit("repository validation report must exist before distribution finalization")
    shutil.copyfile(validation_source, validation_copy)

    identity_path = ROOT / "distribution" / "source-identity.json"
    source_identity = json.loads(identity_path.read_text("utf-8"))
    package_content = {
        "schema": "l9.harness-package-content/v1",
        "package": PROJECT["name"],
        "version": VERSION,
        "sourceIdentityDigest": {
            "algorithm": "sha256",
            "value": sha(identity_path),
        },
        "sourceTreeDigest": source_identity["sourceTreeDigest"],
        "repositoryValidationDigest": file_digest(validation_copy),
        "files": source_identity["files"],
    }
    (DIST / "package-content-manifest.json").write_text(
        json.dumps(package_content, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"l9-harness-{VERSION}",
        "documentNamespace": f"https://quantum-l9.dev/sbom/l9-harness/{VERSION}",
        "packages": [
            {
                "name": "l9-harness",
                "SPDXID": "SPDXRef-Package-l9-harness",
                "versionInfo": VERSION,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": "NOASSERTION",
            }
        ],
    }
    (DIST / "SBOM.spdx.json").write_text(
        json.dumps(sbom, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    provenance = {
        "schema": "l9.build-provenance/v1",
        "package": "l9-harness",
        "version": VERSION,
        "sourceRepository": "Quantum-L9/l9-harness",
        "sourceCommit": "UNKNOWN_REPOSITORY_UNAVAILABLE",
        "sourceIdentityDigest": package_content["sourceIdentityDigest"],
        "sourceTreeDigest": source_identity["sourceTreeDigest"],
        "repositoryValidationDigest": file_digest(validation_copy),
        "buildCommands": [
            "python -m compileall",
            "python -m pytest -q",
            "python scripts/verify_generated.py",
            "python -B scripts/validate_repository.py",
            "uv build --offline",
            "python scripts/finalize_distribution.py",
            "python scripts/verify_distribution.py --write",
        ],
        "networkUsedByRuntimeValidation": False,
        "upstreamAuthorityStatus": "BLOCKED",
        "ruffValidation": "BLOCKED_TOOL_UNAVAILABLE_IN_LOCAL_ENVIRONMENT",
        "mypyValidation": "BLOCKED_TOOL_UNAVAILABLE_IN_LOCAL_ENVIRONMENT",
    }
    (DIST / "provenance.json").write_text(
        json.dumps(provenance, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "scripts/verify_distribution.py", "--dist", "dist", "--write"],
        cwd=ROOT,
        check=True,
    )
    outputs = [
        path for path in sorted(DIST.iterdir()) if path.is_file() and path.name != "SHA256SUMS.txt"
    ]
    (DIST / "SHA256SUMS.txt").write_text(
        "".join(f"{sha(path)}  {path.name}\n" for path in outputs),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
