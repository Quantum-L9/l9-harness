import json

from l9_harness.cli.app import main


def test_doctor_json(capsys, tmp_path):
    rc = main(["--json", "doctor", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc in {0, 40}
    assert out["schema"] == "l9.harness-command-result"
    assert out["authoritative"] is False
