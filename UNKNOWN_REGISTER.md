# Unknown Register

| ID | Unknown | Impact | Resolution evidence required |
|---|---|---|---|
| UNKNOWN-001 | Exact live `Quantum-L9/l9-harness` baseline commit and existing assets | Merge and migration reconciliation | Accessible immutable repository commit and Phase 0 inventory |
| UNKNOWN-002 | Repository license and distribution authorization | Publication and external redistribution | Owner-approved license file |
| UNKNOWN-003 | Immutable Assurance production release tuple | Production Assurance adapter | Release artifact, commit, executable digest, registries, fixtures, SBOM, provenance, and promotion ADR |
| UNKNOWN-004 | Registered production `l9.assurance-plan` schema and digest | Semantic production plan parsing | Assurance schema-registry publication and conformance fixtures |
| UNKNOWN-005 | Approved SDK version, build digests, check versions, and revocation policy | Authoritative observation production | Joint Assurance/SDK producer authorization record |
| UNKNOWN-006 | Authority-published canonicalization vectors | Cross-language and authority canonical-digest claims | Immutable vector bundle and digest |
| UNKNOWN-007 | CI Core hosted shadow-parity evidence and promotion threshold | Production integration decision | Hosted end-to-end comparison report |
| UNKNOWN-008 | Ruff result for this exact source tree | Style and lint gate | Execute pinned Ruff 0.12.12 in a network-enabled or pre-provisioned environment |
| UNKNOWN-009 | mypy strict result for this exact source tree | Static type gate | Execute pinned mypy 1.17.1 in a network-enabled or pre-provisioned environment |

Unknowns are not converted into passing claims. Harness-owned runtime approval does not authorize production cross-repository integration.

## Distribution note

The 2.0.4 source identity proves internal source-to-wheel-to-sdist lineage. It does not resolve `UNKNOWN-001`; the live repository commit remains unavailable and therefore cannot be asserted as the upstream source commit.
