from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src" / "l9_harness"
ALLOWED = {
    "security/subprocesses.py",
    "execution/container_adapter.py",
    "execution/engine.py",
    "execution/process_adapter.py",
}


def test_runtime_subprocess_imports_are_confined() -> None:
    violations: list[str] = []
    for path in ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text("utf-8"))
        imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = imported or any(alias.name == "subprocess" for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported = imported or node.module == "subprocess"
        relative = path.relative_to(ROOT).as_posix()
        if imported and relative not in ALLOWED:
            violations.append(relative)
    assert violations == []
