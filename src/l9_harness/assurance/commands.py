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

from collections.abc import Mapping
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


def command_path(operation: str) -> list[str]:
    """The assurance argv prefix for one harness operation.

    Raises ``KeyError`` for an unknown operation rather than guessing: passing an
    unmapped name straight through is exactly the failure this module exists to
    prevent.
    """
    return list(_COMMAND_PATHS[operation])
