# Validation Report

## Decision

```yaml
validation_status: APPROVED_RECURSIVE_IMPROVEMENT_CONVERGED_HARNESS_OWNED_RUNTIME
version: 2.0.4
architecture_alignment: PASS
assurance_boundary_alignment: PASS
single_ingress_alignment: PASS
source_identity_alignment: PASS
distribution_alignment: PASS
production_cross_repository_integration: BLOCKED_EXTERNAL_AUTHORITY
live_repository_alignment: UNVERIFIABLE
```

## Baseline validation

The delivered 2.0.3 source pack was executed before modification. Its test suite reported 75 passes and 4 failures. The failures were caused by two stale duplicate tree artifacts that contradicted the canonical `FILETREE.md` contract and invalidated tracked-file, source-identity, and distribution-evidence checks.

## Post-fix validation

| Check | Result |
|---|---:|
| Python compilation | PASS |
| Test suite | PASS, 82 tests |
| Repository structural, contract, security, metadata, ingress, and Assurance audit | PASS, 27/27 |
| Generated-artifact drift | PASS, 8/8 governed outputs |
| Harness-owned JSON Schemas | PASS, 21 schemas |
| Canonical source inventory ownership | PASS, `FILETREE.md` only |
| Wheel metadata parity with `pyproject.toml` | PASS |
| Source-distribution canonical tree membership | PASS |
| CLI version parity | PASS |
| Single-ingress deterministic identity and privacy | PASS |
| Public CLI command set preserved | PASS |
| Exact tracked-file path, size, digest, role, and metadata parity | PASS |
| Repository-validation rerun preserves source identity | PASS |
| L9 per-file metadata inheritance | PASS |
| Release-zero SDK check identity set | PASS |
| `PacketEnvelope` prohibition | PASS |
| Assurance and SDK private-import boundaries | PASS |
| Sanitized subprocess confinement | PASS |
| Source identity matches approved source graph | PASS |
| Repository-validation evidence copied and distribution-bound | PASS |
| Wheel runtime and packaged resource bytes match source | PASS |
| Wheel `RECORD` hashes and sizes | PASS |
| Source distribution exact-file parity | PASS |
| Distribution and source-identity schemas | PASS |
| Two independent release builds | PASS |
| Release artifacts byte-identical across independent builds | PASS |
| Isolated wheel installation | PASS |
| Installed module imports | PASS, 139/139 |
| Installed schemas, profiles, templates, and source identity | PASS |
| Delivery ZIP membership, paths, duplicates, symlinks, and byte parity | PASS |
| Secret scan | PASS |
| Ruff 0.12.12 | BLOCKED, exact executable unavailable in offline cache |
| mypy 1.17.1 | BLOCKED, exact executable unavailable in offline cache |

## Identity model

`distribution/source-identity.json` binds the approved source graph. It excludes only its own generated identity, the generated tracked-file index, and mutable repository-validation evidence. The exact validation report is copied to `dist/repository-validation.json` and bound by `repositoryValidationDigest` in the distribution manifest.

## Assurance alignment

Harness remains outside the authoritative CI path. It does not admit evidence, resolve controls or policy, issue verdicts, publish checks, repair repositories, or reinterpret Assurance decisions. External plans, manifests, observations, admitted envelopes, and Assurance outputs remain external-authority artifacts and are not mutated or redefined.

## Honest blockers

- accessible immutable `Quantum-L9/l9-harness` baseline and asset inventory;
- repository license and distribution authorization;
- immutable Assurance production release tuple;
- published production `l9.assurance-plan` schema and vectors;
- trusted SDK producer/build/check tuple;
- authority canonicalization vectors;
- CI Core hosted shadow-parity evidence;
- local execution of pinned Ruff and mypy.

No blocked or unavailable check is represented as passing.
