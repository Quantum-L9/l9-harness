from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from ..domain.errors import ContractError

SUPPORTED_ROUTES = frozenset(
    {
        "assurance",
        "bundle",
        "clean",
        "collect",
        "conformance",
        "corpus",
        "doctor",
        "guidance",
        "init",
        "package",
        "plan",
        "replay",
        "run",
        "verify",
    }
)

_PATH_KEYS = frozenset(
    {
        "assurance_plan",
        "authority",
        "cache",
        "cwd",
        "expected",
        "fixtures",
        "invocations",
        "manifest",
        "observations",
        "outbox",
        "output",
        "plan",
        "profile",
        "remote",
        "repo",
        "root",
        "run_dir",
        "sdk_manifest",
        "source",
        "subject",
        "transported",
    }
)


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, list | tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in sorted(value.items())}
    return str(value)


def _digest(value: Any) -> dict[str, str]:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return {"algorithm": "sha256", "value": hashlib.sha256(encoded).hexdigest()}


@dataclass(frozen=True)
class IngressRequest:
    request_id: str
    objective: str
    mode: str
    inputs: Mapping[str, Any]
    constraints: tuple[str, ...]
    context_refs: tuple[str, ...]
    authority_rules: tuple[str, ...]
    trace_id: str
    validation_profile: str
    output_contract: str
    route: str
    arguments_digest: Mapping[str, str]

    def public_record(self) -> dict[str, Any]:
        return {
            "schema": "l9.harness-single-ingress",
            "schemaVersion": "1.0.0",
            "request_id": self.request_id,
            "objective": self.objective,
            "mode": self.mode,
            "inputs": {
                "argument_names": sorted(self.inputs),
                "arguments_digest": dict(self.arguments_digest),
            },
            "constraints": list(self.constraints),
            "context_refs": list(self.context_refs),
            "authority_rules": list(self.authority_rules),
            "trace_id": self.trace_id,
            "validation_profile": self.validation_profile,
            "output_contract": self.output_contract,
            "route": self.route,
        }


def normalize_cli_request(raw_arguments: list[str], parsed: Mapping[str, Any]) -> IngressRequest:
    route = str(parsed.get("command") or "")
    if route not in SUPPORTED_ROUTES:
        raise ContractError(
            "HARNESS_INGRESS_ROUTE_UNSUPPORTED",
            f"Unsupported Harness route: {route or '<missing>'}",
            details={"route": route},
        )
    normalized_inputs = {
        str(key): _json_value(value)
        for key, value in sorted(parsed.items())
        if key not in {"command", "json"}
    }
    digest = _digest({"route": route, "arguments": normalized_inputs})
    request_id = f"l9.harness-request:sha256:{digest['value']}"
    trace_id = f"l9.harness-trace:sha256:{digest['value']}"
    context_refs = tuple(sorted(key for key in normalized_inputs if key in _PATH_KEYS))
    request = IngressRequest(
        request_id=request_id,
        objective=f"execute:{route}",
        mode="cli",
        inputs=MappingProxyType(normalized_inputs),
        constraints=(
            "fail_closed",
            "non_authoritative",
            "no_direct_module_bypass",
            "preserve_external_contracts",
        ),
        context_refs=context_refs,
        authority_rules=(
            "user_request",
            "harness_public_contracts",
            "external_authority_artifacts",
            "unknown",
        ),
        trace_id=trace_id,
        validation_profile="l9.harness.cli-ingress@1.0.0",
        output_contract="l9.harness-command-result@1.0.0",
        route=route,
        arguments_digest=MappingProxyType(digest),
    )
    validate_ingress(request, raw_arguments)
    return request


def validate_ingress(request: IngressRequest, raw_arguments: list[str]) -> None:
    if not raw_arguments:
        raise ContractError(
            "HARNESS_INGRESS_EMPTY",
            "Harness ingress requires a command.",
        )
    if request.route not in SUPPORTED_ROUTES:
        raise ContractError(
            "HARNESS_INGRESS_ROUTE_UNSUPPORTED",
            f"Unsupported Harness route: {request.route}",
        )
    if request.mode != "cli":
        raise ContractError(
            "HARNESS_INGRESS_MODE_UNSUPPORTED",
            f"Unsupported Harness ingress mode: {request.mode}",
        )
    if request.output_contract != "l9.harness-command-result@1.0.0":
        raise ContractError(
            "HARNESS_INGRESS_OUTPUT_CONTRACT_INVALID",
            "Harness ingress output contract is invalid.",
        )
