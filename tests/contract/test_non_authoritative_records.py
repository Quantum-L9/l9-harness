"""Negative proof that a Harness record can never read as an Assurance verdict.

The `harness_to_assurance` seam is intentionally non-authoritative: the
`l9.assurance-invocation-record` Harness emits describes *that an invocation
happened* (argv, exit code, stdout/stderr digests), and Assurance's own decision
artifact is the only verdict. That intent was previously stated by docs and by
`authoritative: False` literals in the adapters, but nothing proved that a
record claiming authority is refused. These tests pin the seam from the Harness
side: the published schemas admit only `authoritative: false`, the domain
invariant rejects `True`, and the live adapter output validates against the
schema exactly as written.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from l9_harness.cli.app import main
from l9_harness.domain.digests import digest_bytes, digest_canonical
from l9_harness.domain.errors import ContractError
from l9_harness.domain.invariants import prohibit_authoritative_harness

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "v1"


def _registry() -> Registry:
    resources = []
    for path in SCHEMAS.glob("*.schema.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        resources.append((document["$id"], Resource.from_contents(document)))
    return Registry().with_resources(resources)


def _validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def _invocation_record() -> dict:
    """The exact shape `l9_harness.assurance.cli_adapter.invoke` writes."""
    return {
        "schema": "l9.assurance-invocation-record",
        "schemaVersion": "1.0.0",
        "invocationId": "assurance-invocation:00000000-0000-0000-0000-000000000000",
        "argvDigest": digest_canonical(["/usr/bin/l9-assurance", "evaluate"], "assurance-argv"),
        "startedAt": "2026-07-21T00:00:00.000Z",
        "completedAt": "2026-07-21T00:00:01.000Z",
        "exitCode": 0,
        "stdoutDigest": digest_bytes(b""),
        "stderrDigest": digest_bytes(b""),
        "authoritative": False,
    }


def test_invocation_record_schema_admits_only_non_authoritative() -> None:
    validator = _validator("assurance-invocation-record.schema.json")
    record = _invocation_record()
    assert list(validator.iter_errors(record)) == []

    forged = dict(record, authoritative=True)
    errors = [error.message for error in validator.iter_errors(forged)]
    assert errors, "a record claiming authority must fail schema validation"
    assert any("False" in message for message in errors)

    missing = dict(record)
    del missing["authoritative"]
    assert list(validator.iter_errors(missing)), "authoritative is required, not optional"


def test_a_passing_exit_code_is_still_not_a_verdict() -> None:
    """Exit code 0 from Assurance is an execution fact, not an admissible pass."""
    validator = _validator("assurance-invocation-record.schema.json")
    record = _invocation_record()
    assert record["exitCode"] == 0
    assert record["authoritative"] is False
    assert list(validator.iter_errors(dict(record, authoritative=True)))


def test_command_result_schema_admits_only_non_authoritative(capsys, tmp_path) -> None:
    main(["--json", "doctor", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)
    validator = _validator("harness-command-result.schema.json")
    assert result["authoritative"] is False
    assert list(validator.iter_errors(result)) == []
    assert list(validator.iter_errors(dict(result, authoritative=True)))


def test_domain_invariant_rejects_authority() -> None:
    prohibit_authoritative_harness(False)
    with pytest.raises(ContractError):
        prohibit_authoritative_harness(True)
