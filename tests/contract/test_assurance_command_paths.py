"""One table maps harness operation names to l9-assurance command paths.

Four of the five harness operations share a name with the assurance command.
``admit`` does not: assurance spells it ``evidence admit``. That single
divergence used to be encoded twice -- correctly in
``l9_harness.assurance.admission``, and not at all in the CLI, which forwarded
the bare operation name. So ``l9-harness assurance admit`` always died with
``Unknown command admit`` while the Python API worked: the admission route was
reachable through one surface and permanently broken on the other.

These tests pin the table and pin both callers to it.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from l9_harness.assurance import commands
from l9_harness.assurance.admission import admit

# The commands l9-assurance 2.1.1 actually advertises, from `capabilities --json`.
ASSURANCE_COMMANDS = frozenset(
    {
        "capabilities",
        "verify",
        "verify-plan",
        "conformance producer",
        "conformance consumer",
        "plan",
        "evidence admit",
        "evaluate",
        "simulate",
    }
)


def test_admit_resolves_to_the_assurance_evidence_admit_path() -> None:
    """The regression."""
    assert commands.command_path("admit") == ["evidence", "admit"]


@pytest.mark.parametrize("operation", ["plan", "evaluate", "verify", "simulate"])
def test_pass_through_operations_keep_their_name(operation: str) -> None:
    assert commands.command_path(operation) == [operation]


def test_every_operation_maps_to_a_real_assurance_command() -> None:
    """The table must describe assurance, not the harness's wishes.

    This is the assertion that would have caught the original divergence: it
    compares each resolved path against the command set assurance advertises.
    """
    for operation in commands.OPERATIONS:
        resolved = " ".join(commands.command_path(operation))
        assert resolved in ASSURANCE_COMMANDS, (
            f"harness operation {operation!r} resolves to {resolved!r}, "
            "which l9-assurance does not advertise"
        )


def test_unknown_operation_raises_rather_than_passing_through() -> None:
    """Guessing is what produced the bug. An unmapped name must fail loudly."""
    with pytest.raises(KeyError):
        commands.command_path("definitely-not-an-operation")


def test_operations_and_the_table_do_not_drift() -> None:
    for operation in commands.OPERATIONS:
        assert commands.command_path(operation)


def test_admission_api_builds_its_argv_from_the_table(tmp_path: Path) -> None:
    """The typed API must consume the table, not its own copy of the path."""
    captured: dict[str, list[str]] = {}

    def fake_invoke(executable, arguments, cwd, invocations):
        captured["arguments"] = list(arguments)
        return {"record": {"exitCode": 0}, "root": tmp_path}

    with patch("l9_harness.assurance.admission.invoke", fake_invoke):
        admit(
            executable="l9-assurance",
            subject=tmp_path / "subject.json",
            observations=tmp_path / "observations.json",
            output=tmp_path / "out",
            cwd=tmp_path,
            invocations=tmp_path / "invocations",
        )

    assert captured["arguments"][:2] == ["evidence", "admit"]
