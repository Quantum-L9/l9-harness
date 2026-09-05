"""Harness operation name -> l9-assurance CLI command path.

The harness names its assurance operations ``plan``, ``admit``, ``evaluate``,
``verify`` and ``simulate``. Four of those are also the assurance command; the
admission one is not -- assurance spells it ``evidence admit``.

That divergence used to live in two places at once. ``assurance/admission.py``
emitted ``["evidence", "admit", ...]`` and worked, while the CLI forwarded the
operation name verbatim, so ``l9-harness assurance admit`` always died with
``Unknown command admit``: the admission path was reachable through the Python
API and not through the CLI. Both now resolve through this table, so a future
assurance rename cannot fix one caller and miss the other.

The harness stays a subordinate adapter. This maps names; it does not interpret
results, and nothing here decides a verdict.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

#: Operations the harness CLI accepts, in the order it presents them.
OPERATIONS: tuple[str, ...] = ("plan", "admit", "evaluate", "verify", "simulate")

_COMMAND_PATHS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "plan": ("plan",),
        "admit": ("evidence", "admit"),
        "evaluate": ("evaluate",),
        "verify": ("verify",),
        "simulate": ("simulate",),
    }
)


#: Options the harness's own ``assurance`` subparser owns.
#:
#: ``args`` is declared ``nargs=argparse.REMAINDER``, so everything after the
#: operation name is captured verbatim and forwarded to assurance -- including
#: these, when a caller writes them in the wrong order. argparse does not
#: complain; ``--executable`` lands in the forwarded list and the harness
#: silently falls back to its default, running whatever ``l9-assurance`` is on
#: PATH instead of the one the caller named. None of these collide with an
#: assurance flag, so their presence in the forwarded list is unambiguous.
HARNESS_OPTIONS: frozenset[str] = frozenset(
    {
        "--executable",
        "--cwd",
        "--invocations",
        "--authority",
        "--production",
    }
)


def command_path(operation: str) -> list[str]:
    """The assurance argv prefix for one harness operation.

    Raises ``KeyError`` for an unknown operation rather than guessing: passing an
    unmapped name straight through is exactly the failure this module exists to
    prevent.
    """
    return list(_COMMAND_PATHS[operation])


def misplaced_harness_options(args: Sequence[str]) -> list[str]:
    """Harness options found among the arguments forwarded to assurance.

    Returns them in the order given, so the caller can be told exactly which
    ones to move. Matches ``--opt`` and ``--opt=value`` alike.
    """
    found: list[str] = []
    for argument in args:
        name = argument.split("=", 1)[0]
        if name in HARNESS_OPTIONS:
            found.append(name)
    return found
