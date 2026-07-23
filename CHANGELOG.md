# Changelog

## 2.0.4 - Recursive improvement and canonical-pack convergence

### Fixed

- Removed stale `FINAL_TREE.md` and `FINAL_REPO_TREE.md` artifacts that contradicted the canonical `FILETREE.md` contract and caused the delivered baseline tests to fail.
- Regenerated tracked-file and source-identity records from the actual approved source graph.
- Added a repository-level structural gate that rejects duplicate file-tree artifacts.

### Strengthened

- Added wheel metadata parity tests against `pyproject.toml`.
- Added source-distribution tests proving only the canonical file-tree artifact ships.
- Added a public CLI version contract test.
- Rebuilt source, wheel, sdist, schemas, fixtures, SBOM, provenance, validation evidence, and checksums under one 2.0.4 release identity.

### Validation delta

- Baseline delivered pack: 75 passed, 4 failed.
- Revised pack target: all tests and repository gates pass after generated metadata convergence.
- Ruff and mypy remain locally blocked and are not represented as passing.

## 2.0.3 - Recursive leverage and release-evidence closure

### Fixed

- Removed the self-invalidating cycle between repository-validation output and the immutable source identity.
- Added exact tracked-file integrity validation rather than metadata-count-only validation.
- Replaced duplicate final-tree documents with one generated `FILETREE.md`.
- Bound the exact repository-validation report into the distribution manifest.

### Improved

- Added one deterministic CLI ingress with one validation, routing, request-ID, and trace-ID boundary.
- Added provenance and decision records required for ready-to-commit pack reuse.
- Expanded generated-artifact verification to file tree, manifest, source identity, and tracked-file metadata.
- Preserved the full public CLI command set and all Assurance/SDK/CI Core authority boundaries.

### Validation delta

- Test suite increased from 73 to 79 tests before final release proof.
- Repository audit increased from 23 to 26 gates.
- Harness-owned schemas increased from 20 to 21.
- Ruff and mypy remain locally blocked and are not represented as passing.

## 2.0.2 - Recursive alignment and distribution identity

### Fixed

- Removed a duplicate execution-record write in the `run` command.
- Routed the doctor Git probe through the sanitized subprocess boundary.
- Hardened object-store corpus access with HTTPS-first policy, host controls, redirect rejection, and bounded transfer size.
- Added per-file L9 metadata inheritance through the tracked-file index.
- Added a locked Assurance alignment record without copying or redefining Assurance-owned schemas.

### Distribution alignment

- Added a deterministic source identity with the approved source graph and digests.
- Embedded the identical source identity in the wheel and source distribution.
- Added wheel `RECORD`, runtime-byte, resource-byte, and sdist parity verification.
- Added a distribution manifest binding wheel, sdist, schemas, fixtures, CLI snapshot, SBOM, and provenance.
- Split release construction into bounded build and finalization stages.

### Validation delta

- Test suite increased from 64 to 73 tests before final release proof.
- Repository audit increased from 19 to 23 gates.
- Ruff and mypy remain locally blocked and are not represented as passing.

## 2.0.1 - Validation and hardening release

### Fixed

- Replaced the false editable-wheel implementation with a real source-linked PEP 660 wheel.
- Removed mutation of external Assurance plan and SDK capability documents.
- Prohibited guessed Assurance requirements and added requirement-level capability matching.
- Rejected dirty Git subjects and revalidated exact subject identity around every execution.
- Executed SDK checks only in detached isolated clones and preserved declared outputs before teardown.
- Removed unsupported authority-canonical digest claims from preserved external artifacts.
- Hardened observation preflight, archive extraction, bundle membership verification, and corpus synchronization.
- Added executable-digest verification for production Assurance invocations.
- Made generated bindings, schema registry, fixture manifest, and tracked-file index drift-checked artifacts.
- Made release metadata version-derived and required repository validation before packaging.
- Pinned hosted CI quality tools explicitly instead of relying on undeclared ambient executables.

### Validation delta

- Baseline: 50 tests passed.
- Revised: 64 tests passed.
- Repository audit: 19 of 19 checks passed after cache cleanup.
- Ruff and mypy remain locally blocked because their executables were unavailable; hosted workflows now pin exact versions.

### Production blockers retained

- live Harness baseline unavailable;
- immutable Assurance authority tuple unavailable;
- trusted SDK production identity unavailable;
- authority canonicalization vector set unavailable;
- CI Core shadow-parity evidence unavailable.

## 2.0.0 - Generated clean rewrite

- Initial complete Harness v2 clean rewrite aligned to specification 1.2.1.
