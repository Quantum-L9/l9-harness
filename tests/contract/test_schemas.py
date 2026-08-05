import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def test_all_schemas_are_valid():
    for p in (ROOT / "schemas/v1").glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(p.read_text()))


def test_registry_covers_schemas():
    reg = json.loads((ROOT / "schemas/v1/registry.json").read_text())
    files = {
        p.name for p in (ROOT / "schemas/v1").glob("*.schema.json") if p.name != "registry.json"
    }
    listed = {Path(x["path"]).name for x in reg["schemas"]}
    assert files == listed
