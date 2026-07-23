from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from ..application.ingress import IngressRequest, normalize_cli_request
from ..domain.errors import HarnessError
from ..domain.models import CommandResult, VERSION
from .commands import assurance as c_assurance
from .commands import bundle as c_bundle
from .commands import clean as c_clean
from .commands import collect as c_collect
from .commands import conformance as c_conf
from .commands import corpus as c_corpus
from .commands import doctor as c_doctor
from .commands import guidance as c_guidance
from .commands import init as c_init
from .commands import package as c_package
from .commands import plan as c_plan
from .commands import replay as c_replay
from .commands import run as c_run
from .commands import verify as c_verify
from .output import emit


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="l9-harness")
    root.add_argument("--version", action="version", version=VERSION)
    root.add_argument("--json", action="store_true")
    sub = root.add_subparsers(dest="command", required=True)

    command = sub.add_parser("init")
    command.add_argument("repo", nargs="?", default=".")

    command = sub.add_parser("doctor")
    command.add_argument("repo", nargs="?", default=".")

    command = sub.add_parser("plan")
    command.add_argument("--repo", default=".")
    command.add_argument("--profile", required=True)
    command.add_argument("--assurance-plan", required=True)
    command.add_argument("--sdk-manifest", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--production", action="store_true")

    command = sub.add_parser("run")
    command.add_argument("--repo", default=".")
    command.add_argument("--plan", required=True)
    command.add_argument("--sdk-manifest", required=True)
    command.add_argument("--run-dir", required=True)

    command = sub.add_parser("collect")
    command.add_argument("--subject", required=True)
    command.add_argument("--observations", required=True)
    command.add_argument("--output", required=True)

    command = sub.add_parser("package")
    command.add_argument("--source", required=True)
    command.add_argument("--output", required=True)

    command = sub.add_parser("bundle")
    command.add_argument("--root", required=True)
    command.add_argument("--run-key", required=True)
    command.add_argument("--output", required=True)

    command = sub.add_parser("verify")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)

    command = sub.add_parser("replay")
    command.add_argument("--expected", required=True)
    command.add_argument("--actual", required=True)

    command = sub.add_parser("conformance")
    conformance = command.add_subparsers(dest="kind", required=True)
    producer = conformance.add_parser("producer")
    producer.add_argument("--fixtures", required=True)
    consumer = conformance.add_parser("consumer")
    consumer.add_argument("--source", required=True)
    consumer.add_argument("--transported", required=True)

    command = sub.add_parser("assurance")
    command.add_argument(
        "operation",
        choices=["plan", "admit", "evaluate", "verify", "simulate"],
    )
    command.add_argument("--executable", default="l9-assurance")
    command.add_argument("--cwd", default=".")
    command.add_argument("--invocations", default=".l9/harness/assurance-invocations")
    command.add_argument("--authority")
    command.add_argument("--production", action="store_true")
    command.add_argument("args", nargs=argparse.REMAINDER)

    command = sub.add_parser("corpus")
    command.add_argument("action", choices=["pull", "push", "sync", "status"])
    command.add_argument("--remote", required=True)
    command.add_argument("--cache", default=".l9/corpus/cache")
    command.add_argument("--outbox", default=".l9/corpus/outbox")

    command = sub.add_parser("guidance")
    command.add_argument("--root", default=".")
    command.add_argument("--profile", required=True)

    command = sub.add_parser("clean")
    command.add_argument("root", nargs="?", default=".")
    return root


def _dispatch(request: IngressRequest) -> dict[str, Any]:
    inputs = request.inputs
    command_name = request.route
    if command_name == "init":
        return c_init.command(Path(str(inputs["repo"])))
    if command_name == "doctor":
        return c_doctor.command(Path(str(inputs["repo"])))
    if command_name == "plan":
        return c_plan.command(
            Path(str(inputs["repo"])),
            Path(str(inputs["profile"])),
            Path(str(inputs["assurance_plan"])),
            Path(str(inputs["sdk_manifest"])),
            Path(str(inputs["output"])),
            bool(inputs["production"]),
        )
    if command_name == "run":
        return c_run.command(
            Path(str(inputs["repo"])),
            Path(str(inputs["plan"])),
            Path(str(inputs["sdk_manifest"])),
            Path(str(inputs["run_dir"])),
        )
    if command_name == "collect":
        return c_collect.command(
            Path(str(inputs["subject"])),
            Path(str(inputs["observations"])),
            Path(str(inputs["output"])),
        )
    if command_name == "package":
        return c_package.command(
            Path(str(inputs["source"])),
            Path(str(inputs["output"])),
        )
    if command_name == "bundle":
        return c_bundle.command(
            Path(str(inputs["root"])),
            str(inputs["run_key"]),
            Path(str(inputs["output"])),
        )
    if command_name == "verify":
        return c_verify.command(
            Path(str(inputs["root"])),
            Path(str(inputs["manifest"])),
        )
    if command_name == "replay":
        return c_replay.command(
            Path(str(inputs["expected"])),
            Path(str(inputs["actual"])),
        )
    if command_name == "conformance":
        if inputs["kind"] == "producer":
            return c_conf.producer(Path(str(inputs["fixtures"])))
        return c_conf.consumer(
            Path(str(inputs["source"])),
            Path(str(inputs["transported"])),
        )
    if command_name == "assurance":
        return c_assurance.command(
            str(inputs["executable"]),
            [str(inputs["operation"]), *[str(value) for value in inputs["args"]]],
            Path(str(inputs["cwd"])),
            Path(str(inputs["invocations"])),
            Path(str(inputs["authority"])) if inputs["authority"] else None,
            bool(inputs["production"]),
        )
    if command_name == "corpus":
        return c_corpus.command(
            str(inputs["action"]),
            Path(str(inputs["remote"])),
            Path(str(inputs["cache"])),
            Path(str(inputs["outbox"])),
        )
    if command_name == "guidance":
        return c_guidance.command(
            Path(str(inputs["root"])),
            Path(str(inputs["profile"])),
        )
    if command_name == "clean":
        return c_clean.command(Path(str(inputs["root"])))
    raise AssertionError(command_name)


def _result(
    command_name: str,
    data: dict[str, Any],
    request: IngressRequest,
) -> CommandResult:
    status = str(data.pop("status"))
    exit_code = 0 if status == "pass" else 10 if status == "partial" else 40
    artifacts = list(data.pop("artifacts", []))
    limitations = list(data.pop("limitations", []))
    details = data.pop("details", data)
    if not isinstance(details, dict):
        details = {"value": details}
    details = {**details, "ingress": request.public_record()}
    return CommandResult(
        command_name,
        status,
        exit_code,
        artifacts=artifacts,
        limitations=limitations,
        details=details,
        authoritative=bool(data.pop("authoritative", False)),
    )


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    json_anywhere = "--json" in arguments
    arguments = [value for value in arguments if value != "--json"]
    namespace = parser().parse_args(arguments)
    parsed = vars(namespace)
    parsed["json"] = bool(parsed.get("json")) or json_anywhere
    request = normalize_cli_request(arguments, parsed)
    command_name = request.route
    try:
        result = _result(command_name, _dispatch(request), request).to_dict()
        emit(result, bool(parsed["json"]))
        return int(result["exit_code"])
    except HarnessError as error:
        details = error.details | {
            "message": error.message,
            "ingress": request.public_record(),
        }
        result = CommandResult(
            command_name,
            "fail",
            40,
            [error.reason_code],
            details=details,
        ).to_dict()
        emit(result, bool(parsed["json"]))
        return 40
    except Exception as error:
        result = CommandResult(
            command_name,
            "fail",
            50,
            ["HARNESS_INTERNAL_INVARIANT"],
            details={
                "type": type(error).__name__,
                "message": str(error),
                "ingress": request.public_record(),
            },
        ).to_dict()
        emit(result, bool(parsed["json"]))
        return 50


if __name__ == "__main__":
    raise SystemExit(main())
