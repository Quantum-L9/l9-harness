"""The SDK capability manifest has no producer in v0.1.

`validate_sdk_authority` requires seven authority fields and
`producerAuthorization: "approved"`. `l9-ci-sdk` emits none of them -- its
`RepositoryCapabilities` is an unrelated detection result of languages and
package managers. The only instance of the manifest is the development fixture
in this repository, authored here, with placeholder digests.

A self-authored fixture is not evidence that a producer exists. These tests keep
that distinction enforced rather than merely written down: the validation code
is correct and stays, but the fixture must never be usable as production
authority.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l9_harness.contracts.sdk import REQUIRED_AUTHORITY_FIELDS, validate_sdk_authority
from l9_harness.domain.errors import ContractError
from l9_harness.sdk.capability_manifest import inspect_manifest, load_manifest

ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_MANIFEST = ROOT / "fixtures" / "sdk" / "development" / "capability-manifest.json"


def test_the_only_manifest_in_the_tree_is_the_development_fixture() -> None:
    """If a second manifest appears, its provenance needs deciding deliberately."""
    manifests = [
        path
        for path in ROOT.rglob("capability-manifest.json")
        if ".venv" not in path.parts and ".git" not in path.parts
    ]
    assert manifests == [DEVELOPMENT_MANIFEST]


def test_development_manifest_is_not_production_authority() -> None:
    document = json.loads(DEVELOPMENT_MANIFEST.read_text("utf-8"))
    assert document["producerAuthorization"] == "pending"
    assert validate_sdk_authority(document) == ["producerAuthorization:approved"]
    assert inspect_manifest(document)["complete"] is False


def test_loading_the_development_manifest_in_production_mode_fails_closed() -> None:
    """Production mode must refuse the fixture, not quietly accept a placeholder."""
    with pytest.raises(ContractError):
        load_manifest(DEVELOPMENT_MANIFEST, production=True)


def test_development_manifest_still_loads_outside_production_mode() -> None:
    """The development lane keeps working; only the production claim is refused."""
    document = load_manifest(DEVELOPMENT_MANIFEST, production=False)
    assert document["id"] == "l9-ci-sdk"


@pytest.mark.parametrize("field", sorted(REQUIRED_AUTHORITY_FIELDS - {"id", "version"}))
def test_every_authority_field_is_individually_required(field: str) -> None:
    """No field may become optional as a shortcut to marking the manifest complete.

    Relaxing any of these would let an unauthorised or unpinned SDK build be
    treated as approved -- which is precisely the guarantee the missing producer
    means we cannot yet obtain from the real thing.
    """
    document = json.loads(DEVELOPMENT_MANIFEST.read_text("utf-8"))
    document["producerAuthorization"] = "approved"
    assert validate_sdk_authority(document) == []
    del document[field]
    assert field in validate_sdk_authority(document)
