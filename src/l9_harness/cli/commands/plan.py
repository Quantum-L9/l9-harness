from __future__ import annotations
import json
from pathlib import Path
from ...subject.lock import create_subject_lock
from ...planning.run_profile import load_profile
from ...planning.assurance_plan import load_assurance_plan
from ...sdk.capability_manifest import load_manifest
from ...planning.capability_resolution import resolve_plan

def command(repo: Path, profile_path: Path, assurance_plan_path: Path, sdk_manifest_path: Path, output: Path, production: bool=False) -> dict:
    lock = create_subject_lock(repo)
    profile = load_profile(profile_path)
    ap = load_assurance_plan(assurance_plan_path, production=production)
    sdk = load_manifest(sdk_manifest_path, production=production)
    plan = resolve_plan(lock, profile, ap, sdk)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, sort_keys=True, indent=2))
    return {'status': 'pass' if plan['complete'] else 'partial', 'artifacts': [{'path': output.as_posix()}], 'details': {'complete': plan['complete'], 'unresolved': plan['unresolvedRequirements']}}
