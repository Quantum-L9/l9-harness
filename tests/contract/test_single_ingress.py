from __future__ import annotations

import json

from l9_harness.application.ingress import normalize_cli_request
from l9_harness.cli.app import main


def test_ingress_identity_is_deterministic() -> None:
    parsed = {"command": "doctor", "repo": "/tmp/example", "json": True}
    first = normalize_cli_request(["doctor", "/tmp/example"], parsed)
    second = normalize_cli_request(["doctor", "/tmp/example"], parsed)
    assert first.request_id == second.request_id
    assert first.trace_id == second.trace_id
    assert first.public_record() == second.public_record()


def test_ingress_public_record_does_not_emit_argument_values() -> None:
    secret_like_value = "/tmp/not-for-output"
    request = normalize_cli_request(
        ["doctor", secret_like_value],
        {"command": "doctor", "repo": secret_like_value, "json": True},
    )
    encoded = json.dumps(request.public_record(), sort_keys=True)
    assert secret_like_value not in encoded
    assert request.public_record()["inputs"]["argument_names"] == ["repo"]


def test_cli_result_contains_single_ingress_record(capsys, tmp_path) -> None:
    exit_code = main(["--json", "doctor", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code in {0, 40}
    ingress = payload["details"]["ingress"]
    assert ingress["schema"] == "l9.harness-single-ingress"
    assert ingress["route"] == "doctor"
    assert ingress["output_contract"] == "l9.harness-command-result@1.0.0"
