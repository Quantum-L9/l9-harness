import json
import subprocess
from pathlib import Path

from l9_harness.application.execute_run import execute
from l9_harness.domain.digests import digest_bytes, digest_canonical
from l9_harness.subject.lock import create_subject_lock


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_execution_writes_only_to_isolated_workspace(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "a@b.c")
    _git(repo, "config", "user.name", "test")
    (repo / "tracked.txt").write_text("original")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-qm", "baseline")
    lock = create_subject_lock(repo)
    capability_id = "fixture:mutation-test"
    plan = {
        "planId": "harness-plan:sha256:" + "1" * 64,
        "subject": lock["subject"],
        "subjectLockDigest": lock["subjectIdentityDigest"],
        "execution": {"adapter": "process"},
        "complete": True,
        "unresolvedRequirements": [],
        "steps": [{
            "stepId": "harness-step:sha256:" + "2" * 64,
            "kind": "sdk_check",
            "checkRef": "l9.tests",
            "capabilityRef": capability_id,
            "dependsOn": [],
            "required": True,
            "timeoutSeconds": 30,
            "outputContractRef": "l9.observation@1.0.0",
            "network": "denied",
        }],
    }
    manifest = {
        "id": "l9-ci-sdk",
        "capabilities": [{
            "capabilityId": capability_id,
            "checkId": "l9.tests",
            "version": "1.0.0",
            "argv": ["python", "-c", "from pathlib import Path; Path('tracked.txt').write_text('changed'); Path('obs.json').write_text('{}')"],
            "configurationDigest": digest_bytes(b"config"),
            "observationGlobs": ["obs.json"],
            "environmentAllowlist": [],
        }],
    }
    records = execute(plan, manifest, repo, tmp_path / "run")
    assert (repo / "tracked.txt").read_text() == "original"
    assert not (repo / "obs.json").exists()
    copied = tmp_path / "run" / ("2" * 64) / "observations" / "obs.json"
    assert copied.read_text() == "{}"
    assert records[0]["limitations"] == ["network_not_enforced_by_process_adapter"]
