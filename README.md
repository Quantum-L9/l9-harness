# L9 Harness v2

L9 Harness is the deterministic local execution, conformance, replay, and shadow-comparison tool for the Quantum-L9 CI constellation.

## Authority boundary

```text
CI Core orchestrates and publishes.
CI SDK executes checks and emits canonical observations.
Harness exercises public contracts and preserves bytes.
Assurance admits evidence, evaluates controls, and issues decisions.
```

Harness is never a required hop in authoritative Release-zero CI. It does not admit evidence, calculate verdicts, publish GitHub checks, repair repositories, or promote corpus candidates.


## Single ingress

Every CLI command enters through `l9_harness.application.ingress`. The ingress normalizes arguments once, validates the route once, assigns deterministic request and trace identifiers once, and emits only argument names plus an argument digest. Raw argument values are not copied into the public ingress record. Typed internal modules remain composable for tests and embedding and do not become an alternate CLI entrypoint.

## Build provenance

This repository is a controlled clean rewrite from the locked Harness v1.2.1 specification. The target GitHub repository could not be retrieved during this build, so the live baseline commit remains `UNKNOWN_REPOSITORY_UNAVAILABLE`. See `BUILD_AUTHORIZATION.md` and `VALIDATION.md`.

## Current trust status

Harness-owned behavior is implemented and locally validated. Production cross-repository adapters remain fail-closed until immutable upstream authority is supplied:

- Assurance release commit and executable build digest;
- Assurance schema, profile, policy, registry, fixture, SBOM, and provenance digests;
- registered `l9.assurance-plan` schema;
- trusted SDK release/build identity and public invocation contract;
- authority-published canonicalization vectors.

Bundled development fixtures exercise Harness mechanics only. They are not production authority.

## Requirements

- Python 3.11 through 3.13
- `uv`
- Git
- `pytest` for the test suite
- optional external quality tools: Ruff and mypy

The runtime package has no third-party dependencies.

## Install

```bash
uv sync --offline --reinstall
uv run l9-harness --version
uv run l9-harness --help
```

Install the built wheel without dependencies:

```bash
python -m venv .venv-wheel
.venv-wheel/bin/pip install --no-deps dist/l9_harness-2.0.4-py3-none-any.whl
.venv-wheel/bin/l9-harness --version
```

## Validate

The dependency-free acceptance ladder is:

```bash
find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
python scripts/generate_bindings.py
python scripts/update_schema_registry.py
python scripts/update_fixtures.py
python scripts/update_filetree.py
python scripts/update_manifest.py
python scripts/generate_source_identity.py
python scripts/update_tracked_files.py
python scripts/verify_generated.py
python -B scripts/validate_repository.py
python -m compileall -q src tests scripts build_backend.py
python -m pytest -q
python scripts/build_release.py
```

When Ruff and mypy are installed, also run:

```bash
ruff format --check .
ruff check .
mypy src/l9_harness
```

## Local contract exercise

```bash
l9-harness doctor . --json

l9-harness plan \
  --repo . \
  --profile profiles/release-zero-local.yaml \
  --assurance-plan fixtures/assurance/development/assurance-plan.json \
  --sdk-manifest fixtures/sdk/development/capability-manifest.json \
  --output .l9/harness/plan.json \
  --json
```

Production plan parsing requires `--production` and fails closed while authority records remain incomplete.

## Main paths

- `src/l9_harness/`: runtime and CLI;
- `schemas/v1/`: strict Harness-owned JSON Schemas;
- `profiles/`: execution mechanics, never assurance policy;
- `fixtures/`: explicitly labeled development and conformance inputs;
- `tests/`: unit, contract, integration, conformance, replay, adversarial, property, performance, and architecture coverage;
- `docs/requirements/traceability.yaml`: invariant-to-evidence map;
- `RUNBOOK.md`: operation and recovery procedures;
- `MANIFEST.md`: complete source-pack responsibility inventory;
- `FILETREE.md`: deterministic source-pack path inventory;
- `PROVENANCE_MAP.yaml`: source-to-release lineage;
- `DECISION_LOG.md`: material architecture and release decisions;
- `VALIDATION.md`: evidence-backed release status.

## Release artifacts

`python scripts/build_release.py` produces:

- deterministic wheel and source distribution;
- schema and fixture bundles;
- CLI command snapshot;
- package-content manifest;
- SPDX SBOM;
- provenance record;
- byte-preserved repository-validation evidence;
- SHA-256 checksum manifest.

## Verify distribution alignment

```bash
python scripts/generate_source_identity.py
python scripts/update_tracked_files.py
uv build --offline
python scripts/finalize_distribution.py
python scripts/verify_distribution.py --dist dist
```

Inspect `distribution/source-identity.json`, `dist/distribution-manifest.json`, and `dist/distribution-alignment.json`. A successful import alone is not distribution alignment.
