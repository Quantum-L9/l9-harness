from __future__ import annotations

import ast
import hashlib
import importlib
import json
import pkgutil
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "l9_harness"
SCRIPTS = ROOT / "scripts"
PYPROJECT_TOML = "pyproject.toml"
UV_LOCK = "uv.lock"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
RESULTS: list[dict[str, object]] = []


def check(check_id: str, status: str, detail: str, evidence: str = "") -> None:
    RESULTS.append({"check_id": check_id, "status": status, "detail": detail, "evidence": evidence})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected object: {path}")
    return value


def load_tracked_index(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in path.read_text("utf-8").splitlines():
        if line.startswith("  - path: "):
            if current is not None:
                records.append(current)
            current = {"path": json.loads(line.split(": ", 1)[1])}
        elif current is not None and line.startswith("    sha256: "):
            current["sha256"] = line.split(": ", 1)[1]
        elif current is not None and line.startswith("    bytes: "):
            current["bytes"] = int(line.split(": ", 1)[1])
        elif current is not None and line.startswith("    role: "):
            current["role"] = line.split(": ", 1)[1]
        elif current is not None and line.startswith("    meta_ref: "):
            current["meta_ref"] = line.split(": ", 1)[1]
    if current is not None:
        records.append(current)
    return records


def validate_instance(instance: Any, schema_path: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource

        schemas = [load_json(path) for path in (ROOT / "schemas" / "v1").glob("*.schema.json")]
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema)) for schema in schemas
        )
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema, registry=registry)
        return [
            error.message
            for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        ]
    except Exception as error:
        return [f"{type(error).__name__}: {error}"]


def main() -> int:
    RESULTS.clear()
    required = [
        "README.md",
        "AGENTS.md",
        "RUNBOOK.md",
        "ARCHITECTURE.md",
        "SPECIFICATION.md",
        "ROADMAP.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "L9_META.yaml",
        "LICENSE",
        PYPROJECT_TOML,
        UV_LOCK,
        ".python-version",
        "MANIFEST.md",
        "FILETREE.md",
        "CHANGE_SUMMARY.md",
        "VALIDATION.md",
        "UNKNOWN_REGISTER.md",
        "REGRESSION_GUARD.md",
        "TRACEABILITY_MAP.yaml",
        "PROVENANCE_MAP.yaml",
        "DECISION_LOG.md",
        "docs/requirements/SINGLE_INGRESS_CONTRACT.yaml",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    check(
        "V-STRUCT-001", "PASS" if not missing else "FAIL", f"required root files missing: {missing}"
    )

    duplicate_tree_files = [
        path for path in ("FINAL_TREE.md", "FINAL_REPO_TREE.md") if (ROOT / path).exists()
    ]
    check(
        "V-STRUCT-002",
        "PASS" if not duplicate_tree_files else "FAIL",
        f"duplicate file-tree artifacts: {duplicate_tree_files}",
        "canonical=FILETREE.md",
    )

    syntax_errors: list[str] = []
    annotation_errors: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text("utf-8"))
        except SyntaxError as error:
            syntax_errors.append(f"{path.relative_to(ROOT)}:{error.lineno}:{error.msg}")
            continue
        for node in ast.walk(tree):
            if isinstance(
                node, ast.FunctionDef | ast.AsyncFunctionDef
            ) and not node.name.startswith("__"):
                args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                gaps = [
                    arg.arg
                    for arg in args
                    if arg.arg not in {"self", "cls"} and arg.annotation is None
                ]
                if node.returns is None:
                    gaps.append("return")
                if gaps:
                    annotation_errors.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}:{node.name}:{gaps}"
                    )
    check(
        "V-STATIC-001", "PASS" if not syntax_errors else "FAIL", f"syntax errors: {syntax_errors}"
    )
    check(
        "V-STATIC-002",
        "PASS" if not annotation_errors else "FAIL",
        f"public annotation gaps: {annotation_errors[:20]}",
    )

    sys.path.insert(0, str(ROOT / "src"))
    import_errors: list[str] = []
    package = importlib.import_module("l9_harness")
    modules = list(pkgutil.walk_packages(package.__path__, package.__name__ + "."))
    for module in modules:
        try:
            importlib.import_module(module.name)
        except Exception as error:
            import_errors.append(f"{module.name}: {type(error).__name__}: {error}")
    check(
        "V-STATIC-003",
        "PASS" if not import_errors else "FAIL",
        f"import errors: {import_errors}",
        f"modules={len(modules) + 1}",
    )

    source_text = "\n".join(path.read_text("utf-8") for path in SRC.rglob("*.py"))
    prohibited = [
        "PacketEnvelope",
        "shell=True",
        "git apply",
        "apply_patch",
        "create_check_run",
        "merge_pull_request",
        "l9_ci_sdk.",
        "assurance_evaluator",
        "NotImplementedError",
    ]
    hits = [token for token in prohibited if token in source_text]
    check("V-ARCH-001", "PASS" if not hits else "FAIL", f"prohibited runtime symbols: {hits}")
    architecture_failures = []
    if 'requirements = assurance_plan.get("requirements") or' in source_text:
        architecture_failures.append("guessed-assurance-requirements")
    if "_harnessContractComplete" in source_text:
        architecture_failures.append("external-plan-mutation-marker")
    if "authority-canonical-json" in source_text or "assurance-observation" in source_text:
        architecture_failures.append("unverified-authority-canonical-digest")
    check(
        "V-ARCH-002",
        "PASS" if not architecture_failures else "FAIL",
        f"boundary regressions: {architecture_failures}",
    )

    todo_hits: list[str] = []
    for path in SRC.rglob("*.py"):
        for line_no, line in enumerate(path.read_text("utf-8").splitlines(), 1):
            if re.search(r"\b(?:TODO|FIXME|XXX)\b", line):
                todo_hits.append(f"{path.relative_to(ROOT)}:{line_no}")
    check("V-QUALITY-001", "PASS" if not todo_hits else "FAIL", f"unfinished markers: {todo_hits}")

    residue = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if ".venv" not in path.parts
        and any(
            part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
            for part in path.parts
        )
    ]
    check("V-QUALITY-002", "PASS" if not residue else "FAIL", f"cache residue: {residue[:20]}")

    local_path_hits: list[str] = []
    for path in [*SRC.rglob("*.py"), *ROOT.glob("*.toml"), *ROOT.glob("*.yaml")]:
        text = path.read_text("utf-8", errors="ignore")
        if "/mnt/data" in text or "/home/oai" in text:
            local_path_hits.append(path.relative_to(ROOT).as_posix())
    check(
        "V-RELEASE-001",
        "PASS" if not local_path_hits else "FAIL",
        f"embedded local paths: {local_path_hits}",
    )

    project = tomllib.loads((ROOT / PYPROJECT_TOML).read_text("utf-8"))["project"]
    version = project["version"]
    lock_match = re.search(
        r'\[\[package\]\]\s+name = "l9-harness"\s+version = "([^"]+)"',
        (ROOT / UV_LOCK).read_text("utf-8"),
    )
    from l9_harness.domain.models import VERSION

    version_values = {
        "pyproject": version,
        UV_LOCK: lock_match.group(1) if lock_match else "MISSING",
        "runtime": VERSION,
    }
    check(
        "V-RELEASE-002",
        "PASS" if len(set(version_values.values())) == 1 else "FAIL",
        f"version identities: {version_values}",
    )

    # Exact tool pins now live in pyproject.toml's [dependency-groups].dev (so
    # Dependabot's uv ecosystem can see and bump them via uv.lock), not as
    # literal strings in workflow YAML -- ci.yml just runs `uv sync --locked`
    # against whatever pyproject.toml + uv.lock declare. This check verifies
    # the pins are still exact (== , not a range) at their new source of
    # truth, plus that CI actually installs from the lock deterministically.
    workflow_text = "\n".join(
        path.read_text("utf-8") for path in sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    )
    dev_group = (
        tomllib.loads((ROOT / PYPROJECT_TOML).read_text("utf-8"))
        .get("dependency-groups", {})
        .get("dev", [])
    )
    required_tools = {"ruff", "mypy", "pytest", "jsonschema"}
    pinned_tools = {
        re.match(r"([A-Za-z0-9_.-]+)==", dep).group(1)
        for dep in dev_group
        if re.match(r"([A-Za-z0-9_.-]+)==", dep)
    }
    missing_pins = sorted(required_tools - pinned_tools)
    if "uv sync --locked" not in workflow_text:
        missing_pins.append("uv sync --locked")
    check(
        "V-CI-001",
        "PASS" if not missing_pins else "FAIL",
        f"missing exact CI tool pins: {missing_pins}",
    )

    schema_errors: list[str] = []
    try:
        from jsonschema import Draft202012Validator

        for path in sorted((ROOT / "schemas" / "v1").glob("*.schema.json")):
            Draft202012Validator.check_schema(load_json(path))
    except Exception as error:
        schema_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-SCHEMA-001",
        "PASS" if not schema_errors else "FAIL",
        f"schema validation: {schema_errors or 'all schemas valid'}",
    )

    registry = load_json(ROOT / "schemas" / "v1" / "registry.json")
    registry_errors = [
        entry["path"]
        for entry in registry["schemas"]
        if sha256(ROOT / entry["path"]) != entry["digest"]["value"]
    ]
    check(
        "V-SCHEMA-002",
        "PASS" if not registry_errors else "FAIL",
        f"schema registry digest mismatches: {registry_errors}",
    )

    profile_errors: list[str] = []
    for path in sorted((ROOT / "profiles").glob("*.yaml")):
        profile_errors.extend(
            f"{path.name}:{error}"
            for error in validate_instance(
                load_json(path), ROOT / "schemas/v1/harness-run-profile.schema.json"
            )
        )
    check(
        "V-SCHEMA-003",
        "PASS" if not profile_errors else "FAIL",
        f"profile instance errors: {profile_errors}",
    )

    from l9_harness.contracts.assurance import plan_contract_complete
    from l9_harness.observations.validate import validate_observation

    plan = load_json(ROOT / "fixtures/assurance/development/assurance-plan.json")
    plan_complete, plan_missing = plan_contract_complete(plan)
    observation_errors = []
    for path in sorted((ROOT / "fixtures/sdk/valid").glob("*.json")):
        valid, reasons, _ = validate_observation(path, load_json(path)["subject"])
        if not valid:
            observation_errors.append(f"{path.name}:{reasons}")
    fixture_errors = [] if plan_complete else plan_missing
    fixture_errors.extend(observation_errors)
    check(
        "V-FIXTURE-001",
        "PASS" if not fixture_errors else "FAIL",
        f"contract fixture errors: {fixture_errors}",
    )

    manifest = load_json(ROOT / "fixtures" / "manifest.json")
    manifest_errors = []
    for item in manifest["files"]:
        path = ROOT / "fixtures" / item["path"]
        if sha256(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            manifest_errors.append(item["path"])
    check(
        "V-FIXTURE-002",
        "PASS" if not manifest_errors else "FAIL",
        f"fixture manifest mismatches: {manifest_errors}",
    )

    secret_patterns = (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    )
    secret_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".venv", "dist", ".git"} for part in path.parts):
            continue
        try:
            text = path.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in secret_patterns):
            secret_hits.append(path.relative_to(ROOT).as_posix())
    check("V-SEC-001", "PASS" if not secret_hits else "FAIL", f"secret marker hits: {secret_hits}")

    help_result = subprocess.run(
        [sys.executable, "-m", "l9_harness", "--help"],
        cwd=ROOT,
        env={
            "PYTHONPATH": str(ROOT / "src"),
            "PATH": __import__("os").environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
    )
    check(
        "V-CLI-001",
        "PASS" if help_result.returncode == 0 else "FAIL",
        help_result.stderr or "CLI help rendered",
    )

    editable_errors: list[str] = []
    try:
        sys.path.insert(0, str(ROOT))
        import build_backend

        with tempfile.TemporaryDirectory() as directory:
            wheel = Path(directory) / build_backend.build_editable(directory)
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
                pth = [name for name in names if name.endswith("_editable.pth")]
                if len(pth) != 1 or "l9_harness/__init__.py" in names:
                    editable_errors.append("editable wheel does not use a source .pth")
    except Exception as error:
        editable_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-PACKAGE-001",
        "PASS" if not editable_errors else "FAIL",
        f"editable backend: {editable_errors or 'real source-linked wheel'}",
    )

    subprocess_import_violations: list[str] = []
    subprocess_allowed = {
        "security/subprocesses.py",
        "execution/container_adapter.py",
        "execution/engine.py",
        "execution/process_adapter.py",
    }
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = imported or any(alias.name == "subprocess" for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported = imported or node.module == "subprocess"
        relative = path.relative_to(SRC).as_posix()
        if imported and relative not in subprocess_allowed:
            subprocess_import_violations.append(relative)
    check(
        "V-SEC-002",
        "PASS" if not subprocess_import_violations else "FAIL",
        f"runtime subprocess boundary violations: {subprocess_import_violations}",
    )

    tracked_text = (ROOT / "docs" / "requirements" / "tracked-files.yaml").read_text("utf-8")
    tracked_paths = tracked_text.count("  - path: ")
    tracked_meta_refs = tracked_text.count("    meta_ref: L9_META.yaml")
    meta_coverage = (
        "metadata_ref: L9_META.yaml" in tracked_text
        and "metadata_inheritance: every_entry" in tracked_text
        and tracked_paths == tracked_meta_refs
        and tracked_paths > 0
    )
    check(
        "V-META-001",
        "PASS" if meta_coverage else "FAIL",
        f"L9 metadata coverage: files={tracked_paths}, meta_refs={tracked_meta_refs}",
    )

    tracked_index_errors: list[str] = []
    try:
        from update_tracked_files import tracked_records

        expected_tracked = tracked_records(ROOT)
        actual_tracked = load_tracked_index(ROOT / "docs" / "requirements" / "tracked-files.yaml")
        if actual_tracked != expected_tracked:
            # The comparison is over whole records, so counts can agree while
            # content differs -- reporting only lengths produced the useless
            # "expected=311 actual=311". Name what actually diverged: paths that
            # appeared or vanished, else the records whose content drifted.
            expected_paths = {record["path"] for record in expected_tracked}
            actual_paths = {record["path"] for record in actual_tracked}
            added = sorted(expected_paths - actual_paths)
            removed = sorted(actual_paths - expected_paths)
            expected_by_path = {record["path"]: record for record in expected_tracked}
            actual_by_path = {record["path"]: record for record in actual_tracked}
            changed = sorted(
                path
                for path in expected_paths & actual_paths
                if expected_by_path[path] != actual_by_path[path]
            )
            detail = "; ".join(
                part
                for part in (
                    f"missing from index: {added}" if added else "",
                    f"stale in index: {removed}" if removed else "",
                    f"content drifted: {changed}" if changed else "",
                )
                if part
            )
            tracked_index_errors.append(
                "tracked index mismatch "
                f"(expected={len(expected_tracked)} actual={len(actual_tracked)}): "
                f"{detail or 'record ordering differs'}. "
                "Regenerate with scripts/update_tracked_files.py."
            )
    except Exception as error:
        tracked_index_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-META-002",
        "PASS" if not tracked_index_errors else "FAIL",
        f"tracked-file integrity: {tracked_index_errors or 'exact'}",
    )

    source_identity_errors: list[str] = []
    try:
        scripts_path = str(ROOT / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        from release_identity import source_records, source_tree_digest

        identity_path = ROOT / "distribution" / "source-identity.json"
        identity = load_json(identity_path)
        records = source_records(ROOT)
        if identity.get("sourceFileCount") != len(records):
            source_identity_errors.append("file-count")
        if identity.get("sourceTreeDigest") != source_tree_digest(records):
            source_identity_errors.append("tree-digest")
        if identity.get("files") != records:
            source_identity_errors.append("file-records")
        identity_schema_errors = validate_instance(
            identity,
            ROOT / "schemas/v1/source-identity.schema.json",
        )
        source_identity_errors.extend(identity_schema_errors)
    except Exception as error:
        source_identity_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-RELEASE-003",
        "PASS" if not source_identity_errors else "FAIL",
        f"source identity errors: {source_identity_errors}",
    )

    assurance_alignment_errors: list[str] = []
    from l9_harness.contracts.observations import RELEASE_ZERO_CHECKS

    expected_checks = {
        "l9.repository-metadata",
        "l9.transport-packet",
        "l9.sdk-validation",
        "l9.lint",
        "l9.tests",
        "l9.mandatory-findings",
    }
    if set(RELEASE_ZERO_CHECKS) != expected_checks:
        assurance_alignment_errors.append("release-zero-check-set")
    if "PacketEnvelope" in source_text:
        assurance_alignment_errors.append("packet-envelope")
    if "assurance_evaluator" in source_text or "@l9/assurance" in source_text:
        assurance_alignment_errors.append("assurance-private-import")
    check(
        "V-ASSURANCE-001",
        "PASS" if not assurance_alignment_errors else "FAIL",
        f"Assurance boundary alignment: {assurance_alignment_errors or 'locked'}",
    )

    ingress_errors: list[str] = []
    try:
        from l9_harness.application.ingress import SUPPORTED_ROUTES

        expected_routes = {
            "assurance",
            "bundle",
            "clean",
            "collect",
            "conformance",
            "corpus",
            "doctor",
            "guidance",
            "init",
            "package",
            "plan",
            "replay",
            "run",
            "verify",
        }
        app_text = (SRC / "cli" / "app.py").read_text("utf-8")
        if set(SUPPORTED_ROUTES) != expected_routes:
            ingress_errors.append("route-set")
        if "normalize_cli_request" not in app_text or "_dispatch(request)" not in app_text:
            ingress_errors.append("cli-bypass")
        ingress_contract = ROOT / "docs" / "requirements" / "SINGLE_INGRESS_CONTRACT.yaml"
        if not ingress_contract.is_file():
            ingress_errors.append("contract-missing")
    except Exception as error:
        ingress_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-INGRESS-001",
        "PASS" if not ingress_errors else "FAIL",
        f"single-ingress enforcement: {ingress_errors or 'locked'}",
    )

    evidence_scope_errors: list[str] = []
    try:
        identity = load_json(ROOT / "distribution" / "source-identity.json")
        expected_evidence = ["docs/validation/repository-validation.json"]
        if identity.get("mutableEvidenceExclusions") != expected_evidence:
            evidence_scope_errors.append("mutable-evidence-exclusion")
        if identity.get("identityScope") != "approved-source-graph":
            evidence_scope_errors.append("identity-scope")
    except Exception as error:
        evidence_scope_errors.append(f"{type(error).__name__}: {error}")
    check(
        "V-RELEASE-004",
        "PASS" if not evidence_scope_errors else "FAIL",
        f"source/evidence identity separation: {evidence_scope_errors or 'explicit'}",
    )

    output = ROOT / "docs" / "validation" / "repository-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"schema": "l9.repository-validation/v1", "checks": RESULTS}, sort_keys=True, indent=2
        )
        + "\n"
    )
    failed = [item for item in RESULTS if item["status"] == "FAIL"]
    print(
        json.dumps(
            {
                "checks": len(RESULTS),
                "passed": len(RESULTS) - len(failed),
                "failed": len(failed),
                "report": output.as_posix(),
            },
            indent=2,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
