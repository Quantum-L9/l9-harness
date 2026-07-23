from __future__ import annotations

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path


def resource_root() -> Traversable:
    packaged = files("l9_harness").joinpath("resources")
    if packaged.joinpath("schemas").is_dir():
        return packaged
    return Path(__file__).resolve().parents[2]


def schema_path(name: str) -> Traversable:
    return resource_root().joinpath("schemas", "v1", name)


def profile_path(name: str) -> Traversable:
    return resource_root().joinpath("profiles", name)


def source_identity_path() -> Traversable:
    return resource_root().joinpath("distribution", "source-identity.json")
