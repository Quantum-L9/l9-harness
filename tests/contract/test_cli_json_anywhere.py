import json

from l9_harness.cli.app import main


def test_json_flag_after_command(capsys, tmp_path):
    rc = main(["doctor", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc in {0, 40}
    assert payload["authoritative"] is False
