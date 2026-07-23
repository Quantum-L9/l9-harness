# L9 Harness v2 Runbook

## 1. Preflight

1. Work from an immutable Git revision.
2. Run `l9-harness doctor <repo> --json`.
3. Verify the Assurance and SDK authority records. Production mode rejects `UNKNOWN` values.
4. Confirm the run profile denies network unless a reviewed adapter explicitly requires it.
5. Preserve the subject lock before invoking any SDK capability.

## 2. Bootstrap

```bash
uv sync --offline --reinstall
uv run l9-harness init <repo> --json
uv run l9-harness doctor <repo> --json
```

`init` writes only `.l9/harness/config.yaml` beneath the selected repository. It does not alter tracked source files.

## 3. Local contract exercise

```bash
uv run l9-harness plan \
  --repo <repo> \
  --profile profiles/release-zero-local.yaml \
  --assurance-plan fixtures/assurance/development/assurance-plan.json \
  --sdk-manifest fixtures/sdk/development/capability-manifest.json \
  --output <repo>/.l9/harness/plan.json \
  --json
```

The bundled fixtures prove Harness mechanics only. They are not trusted Assurance or SDK releases.

## 4. Artifact lifecycle

```text
SDK observations
  -> artifacts/observations/

Supporting files
  -> artifacts/supporting/

Assurance admission invocation
  -> .l9/harness/assurance-invocations/<id>/admission/
  -> .l9/harness/assurance-invocations/<id>/admission/accepted/

Assurance evaluation
  -> consumes that exact accepted directory
  -> .l9/harness/assurance-invocations/<id>/evaluation/output/

Publication copy
  -> byte-preserved copy to artifacts/assurance/
```

Every copied observation, admitted envelope, and Assurance output carries raw SHA-256 provenance. Harness never reconstructs canonical upstream artifacts.

## 5. Production authority gates

Production mode requires all of the following:

- immutable Assurance release tuple;
- registered Assurance plan schema and fixture digest;
- immutable SDK release/build identity;
- approved producer and check versions;
- published canonicalization vectors;
- exact subject and registry digests.

A missing gate is a hard stop. Development fixtures must never be promoted by configuration trickery.

## 6. Corpus operation

The central corpus uses separate locations:

```text
.l9/corpus/cache/   pulled immutable snapshots
.l9/corpus/outbox/  locally generated candidates
```

Commands:

```bash
l9-harness corpus pull --remote <remote> --cache .l9/corpus/cache --outbox .l9/corpus/outbox
l9-harness corpus push --remote <remote> --cache .l9/corpus/cache --outbox .l9/corpus/outbox
l9-harness corpus sync --remote <remote> --cache .l9/corpus/cache --outbox .l9/corpus/outbox
l9-harness corpus status --remote <remote> --cache .l9/corpus/cache --outbox .l9/corpus/outbox
```

Candidates are never auto-promoted.

## 7. Recovery

- **Subject changed:** discard revision-bound observations and create a fresh subject lock.
- **Digest mismatch:** quarantine the artifact; never rewrite or reconstruct it.
- **Admission failure:** preserve exit code, stdout, stderr, arguments digest, and invocation record.
- **Replay mismatch:** block promotion and inspect the first raw or semantic delta.
- **Corpus conflict:** retain both candidates in outbox; never auto-merge.
- **Unsafe archive or path:** stop and preserve diagnostics outside the attempted extraction root.
- **Missing upstream authority:** use experimental opaque capture or stop; never silently downgrade.
- **Assurance unavailable:** do not issue or emulate a verdict.
- **SDK unavailable:** do not substitute the diagnostic fallback as Release-zero evidence.

## 8. Validation and release

```bash
python -m compileall -q src tests scripts build_backend.py
python scripts/generate_bindings.py
python scripts/verify_generated.py
PYTHONPATH=src python scripts/validate_repository.py
PYTHONPATH=src python -m pytest
PYTHONPATH=src python scripts/build_release.py
```

Optional external checks:

```bash
ruff format --check .
ruff check .
mypy src/l9_harness
```

Inspect `dist/SHA256SUMS.txt`, `dist/provenance.json`, and `dist/package-content-manifest.json` before publication. This pack does not authorize publication.

## 9. Distribution alignment recovery

Run these stages separately so a failure is attributable:

```bash
python -m pytest -q
find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
python -B scripts/validate_repository.py
python scripts/generate_source_identity.py
python scripts/update_tracked_files.py
python scripts/verify_generated.py
rm -rf dist && mkdir dist
uv build --offline
python scripts/finalize_distribution.py
python scripts/verify_distribution.py --dist dist
```

- **Source identity mismatch:** regenerate only after all approved source edits and validation reports are final.
- **Wheel mismatch:** reject the wheel; do not patch the archive.
- **Wheel `RECORD` mismatch:** reject the wheel as corrupted.
- **Sdist mismatch:** rebuild from the approved source root; do not copy missing files into the archive.
- **Distribution digest mismatch:** rebuild the entire distribution set from the same source identity.
