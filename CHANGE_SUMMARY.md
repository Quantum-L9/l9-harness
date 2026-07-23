# Change Summary

## Release

`l9-harness` 2.0.4 applies the recursive L9 improvement contract to the 2.0.3 repository and wheel as one coupled release system. It preserves the Harness role, public CLI, schemas, Assurance boundary, SDK boundary, deterministic build model, and fail-closed production gates.

## Baseline defects confirmed

1. The delivered pack retained `FINAL_TREE.md` and `FINAL_REPO_TREE.md` even though its own contract and tests required one canonical `FILETREE.md`.
2. The stale tree artifacts caused source identity, tracked-file integrity, repository validation, and distribution-validation tests to fail.
3. Wheel metadata and source-distribution tree ownership were not independently asserted as public package contracts.
4. The public `--version` behavior existed but lacked a regression test.

## Repairs

- Removed the stale tree artifacts and retained `FILETREE.md` as the only generated source inventory.
- Added repository gate `V-STRUCT-002` to prevent duplicate tree artifacts from returning.
- Added wheel metadata, sdist tree ownership, and CLI version contract tests.
- Bumped the release identity to 2.0.4 and regenerated every governed artifact from the finalized source graph.

## Preserved boundaries

- Harness remains outside authoritative CI.
- SDK remains the observation producer.
- Assurance remains evidence-admission and decision authority.
- CI Core remains decision publisher.
- TransportPacket remains an SDK-owned repository check, not a Harness artifact envelope.
- PacketEnvelope remains prohibited.
- Diagnostic fallback remains non-authoritative.

## Remaining external blockers

The live Harness baseline, repository distribution authorization, immutable Assurance release, trusted SDK tuple, authority canonicalization vectors, CI Core shadow evidence, Ruff, and mypy remain explicitly unresolved.
