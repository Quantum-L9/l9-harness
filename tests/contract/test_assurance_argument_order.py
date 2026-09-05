"""Harness options must not be forwarded to assurance as if they were its own.

``l9-harness assurance`` declares ``args`` as ``nargs=argparse.REMAINDER``, so
everything after the operation name is captured verbatim and handed to
assurance. argparse raises nothing when a caller writes a harness option there,
so ``l9-harness assurance plan --executable /path/to/l9-assurance ...`` put
``--executable`` into the forwarded list and the harness fell back to its
default, running whatever ``l9-assurance`` was on PATH.

In a sandbox with nothing of that name installed this surfaced as a clean
``FileNotFoundError``. On a host where some *other* ``l9-assurance`` is on PATH
it would have run that one instead, recorded the invocation as authoritative
evidence of an assurance run, and said nothing -- while the record's
``argvDigest`` named only the bare string ``l9-assurance``, so the record could
not even show which binary executed.

Both halves are closed here: the misordering is refused, and the executable is
resolved to a concrete path before invocation so the record binds it.
"""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

import pytest

from l9_harness.assurance import cli_adapter, commands
from l9_harness.cli import app
from l9_harness.cli.commands import assurance as cli_assurance
from l9_harness.domain.errors import HarnessError
from l9_harness.domain.reason_codes import ReasonCode


def _stub_executable(directory: Path, name: str = "l9-assurance") -> Path:
    path = directory / name
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


class TestMisplacedOptionDetection:
    @pytest.mark.parametrize(
        "option",
        ["--executable", "--cwd", "--invocations", "--authority", "--production"],
    )
    def test_each_harness_option_is_detected_in_the_forwarded_args(self, option: str) -> None:
        assert commands.misplaced_harness_options(["plan", option, "x"]) == [option]

    def test_the_equals_form_is_detected(self) -> None:
        assert commands.misplaced_harness_options(["--executable=/bin/true"]) == ["--executable"]

    def test_assurance_flags_are_not_flagged(self) -> None:
        """A false positive here would break every correct invocation.

        None of assurance's own flags collide with a harness option, which is
        what makes the detection unambiguous rather than a heuristic.
        """
        assert (
            commands.misplaced_harness_options(
                [
                    "--root",
                    "/bundle",
                    "--profile",
                    "l9.pull-request",
                    "--policy",
                    "l9.organization-default@1.0.0",
                    "--subject",
                    "subject.json",
                    "--evidence",
                    "accepted",
                    "--output",
                    "decision",
                    "--received-at",
                    "2026-09-05T00:00:00Z",
                    "--evaluation-time",
                    "2026-09-05T00:00:00Z",
                    "--input",
                    "admit-input",
                    "--waivers",
                    "waivers.json",
                ]
            )
            == []
        )

    def test_the_detected_set_is_exactly_what_the_parser_declares(self) -> None:
        """Bound to the real parser, not to a second copy of the list.

        Comparing ``HARNESS_OPTIONS`` against a literal in this file proves
        nothing: adding a sixth option to the ``assurance`` subparser would
        reintroduce the defect this module exists to prevent, with both the
        frozenset and the literal unchanged and the suite green. So the
        declaration is read off the parser itself.

        argparse exposes no public accessor for a subparser, hence the private
        attributes. A layout change here fails loudly rather than silently
        passing, which is the property that matters.
        """
        root = app.parser()
        subparsers = [
            action for action in root._actions if isinstance(action, argparse._SubParsersAction)
        ]
        assert len(subparsers) == 1, "parser layout changed; update this test"
        assurance = subparsers[0].choices["assurance"]
        declared = {
            option
            # argparse adds its own help action. Forwarding ``--help`` to
            # assurance is what a caller writing it after the operation wants,
            # so it is deliberately not a harness option.
            for action in assurance._actions
            if not isinstance(action, argparse._HelpAction)
            for option in action.option_strings
            if option.startswith("--")
        }
        assert declared == commands.HARNESS_OPTIONS


class TestCommandRefusesMisordering:
    def test_a_forwarded_harness_option_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(HarnessError) as caught:
            cli_assurance.command(
                "l9-assurance",
                ["--executable", str(tmp_path / "l9-assurance"), "--root", "/bundle"],
                tmp_path,
                tmp_path / "invocations",
            )
        assert caught.value.reason_code == ReasonCode.INPUT_INVALID
        assert "--executable" in caught.value.message
        assert caught.value.details["misplaced_options"] == ["--executable"]

    def test_the_refusal_happens_before_anything_is_executed(self, tmp_path: Path) -> None:
        invocations = tmp_path / "invocations"
        with pytest.raises(HarnessError):
            cli_assurance.command(
                "l9-assurance",
                ["--production"],
                tmp_path,
                invocations,
            )
        assert not invocations.exists()


class TestExecutableResolution:
    def test_an_unresolvable_bare_name_is_a_caller_error(self, tmp_path: Path) -> None:
        """Not an internal-invariant breach.

        This previously escaped as FileNotFoundError, which the CLI reports as
        exit 50 HARNESS_INTERNAL_INVARIANT -- blaming the harness for what the
        caller got wrong.
        """
        with pytest.raises(HarnessError) as caught:
            cli_assurance.command(
                "definitely-not-on-path-l9-assurance",
                ["--root", "/bundle"],
                tmp_path,
                tmp_path / "invocations",
            )
        assert caught.value.reason_code == ReasonCode.INPUT_INVALID
        assert "not on PATH" in caught.value.message

    def test_a_named_path_that_does_not_exist_is_a_caller_error(self, tmp_path: Path) -> None:
        with pytest.raises(HarnessError) as caught:
            cli_assurance.command(
                str(tmp_path / "nope" / "l9-assurance"),
                ["--root", "/bundle"],
                tmp_path,
                tmp_path / "invocations",
            )
        assert caught.value.reason_code == ReasonCode.INPUT_INVALID
        assert "does not exist" in caught.value.message

    def test_the_record_binds_the_resolved_path_not_the_bare_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The invocation record must say which binary ran."""
        bindir = tmp_path / "bin"
        bindir.mkdir()
        stub = _stub_executable(bindir)
        monkeypatch.setenv("PATH", str(bindir) + os.pathsep + os.environ["PATH"])

        from l9_harness.domain.digests import digest_canonical

        result = cli_assurance.command(
            "l9-assurance",
            ["plan"],
            tmp_path,
            tmp_path / "invocations",
        )
        # Resolving the bare name must produce the same digest as naming the
        # resolved path outright; the bare string must not.
        assert result["details"]["argvDigest"] == digest_canonical(
            [str(stub.resolve()), "plan"], "assurance-argv"
        )
        assert result["details"]["argvDigest"] != digest_canonical(
            ["l9-assurance", "plan"], "assurance-argv"
        )
        assert result["authoritative"] is False

    def test_binding_is_enforced_by_the_module_that_writes_the_digest(self, tmp_path: Path) -> None:
        """Not only by the CLI.

        ``invoke`` writes ``argvDigest``, so it owns the invariant that the
        record binds what ran. Enforcing it only in the CLI left the library
        entry points -- ``capture_plan``, ``admit``, ``simulate``, ``evaluate``
        -- reaching ``invoke`` with an unresolved name and producing a record
        that bound nothing.
        """
        invocations = tmp_path / "invocations"
        with pytest.raises(HarnessError) as caught:
            cli_adapter.invoke(
                "definitely-not-on-path-l9-assurance",
                ["--root", "/bundle"],
                tmp_path,
                invocations,
            )
        assert caught.value.reason_code == ReasonCode.INPUT_INVALID
        # And no invocation directory was left behind looking like an attempt.
        assert not invocations.exists()

    def test_resolution_is_idempotent_on_an_absolute_path(self, tmp_path: Path) -> None:
        """The CLI resolves, then passes the result to ``invoke``, which
        resolves again. The second pass must not change the path, or authority
        verification and the invocation would disagree about which file ran."""
        stub = _stub_executable(tmp_path)
        once = cli_adapter.resolve_executable(str(stub))
        assert cli_adapter.resolve_executable(once) == once
        assert once == str(stub.resolve())
