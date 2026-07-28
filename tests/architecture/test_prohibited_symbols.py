import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src/l9_harness"


def test_no_shell_true():
    assert "shell=True" not in "\n".join(p.read_text() for p in ROOT.rglob("*.py"))


def test_no_packet_envelope_symbol_in_runtime():
    assert "PacketEnvelope" not in "\n".join(p.read_text() for p in ROOT.rglob("*.py"))


def test_no_verdict_assignment():
    for p in ROOT.rglob("*.py"):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign | ast.AnnAssign):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                assert all(
                    not (isinstance(t, ast.Name) and t.id.lower() == "verdict") for t in targets
                )
