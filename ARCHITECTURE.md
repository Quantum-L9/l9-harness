# L9 Harness v2 Architecture

## Role

Harness owns deterministic local coordination, exact-subject locking, public SDK invocation, byte-preserving observation collection, Assurance-compatible artifact export, external non-authoritative Assurance invocation, conformance, replay, central corpus synchronization, and deterministic guidance projections.

## Boundary map

```text
Git revision -> Subject Lock
Public Assurance plan + SDK capability contract -> bounded Harness Plan
SDK execution -> immutable observation files
Harness export -> observations/ + supporting/
External Assurance CLI -> admission/accepted -> evaluation outputs
Harness run bundle -> replay and audit support only
```

## State ownership

- Harness owns run profiles, plans, execution records, observation indexes, input manifests, run-bundle manifests, conformance reports, replay records, corpus snapshots, and guidance manifests.
- SDK owns check semantics and canonical observations.
- Assurance owns schemas for its protocol, registries, admission, controls, policy, waivers, unknowns, decisions, and attestations.
- CI Core owns hosted orchestration and publication.

## Dependency direction

Harness may invoke pinned public CLIs or consume published schemas and fixtures. It must not import implementation packages from Assurance, CI Core, PR Repair, Debt Resolver, Debt Intelligence, or the SDK private surface.

## Determinism

Semantic digests exclude execution IDs, timestamps, logs, and resource usage. Raw-byte digests and authority-defined canonical payload digests remain separate. Deterministic ZIPs use fixed timestamps, sorted paths, normalized permissions, and no absolute paths.

## Failure model

A check failure is an SDK observation. Missing output or an infrastructure failure makes the Harness run partial or failed; Harness never converts either into an Assurance verdict.

## L9 applicability

Harness is not a runtime node. Gate-only node egress, node-to-node dispatch, `derive_or_with_hop`, and runtime `TransportPacket` routing do not govern its local filesystem handoff to Assurance. `PacketEnvelope` remains prohibited. The `l9.transport-packet` identity remains an SDK observation about the target repository.

Repository metadata is carried by `L9_META.yaml` and inherited by every entry in `docs/requirements/tracked-files.yaml`. Strict external schemas and generated artifacts are indexed rather than mutated inline.

## Distribution identity

The source graph is bound by `distribution/source-identity.json`. The same bytes are packaged in the wheel and sdist. Generated release artifacts are bound by `dist/distribution-manifest.json`, while `dist/distribution-alignment.json` records byte-level parity results. See ADR-010.

## Single-ingress command boundary

The CLI has one normalized ingress in `l9_harness.application.ingress`. Parsing may expose multiple commands, but routing occurs only after the ingress validates a supported route and constructs a deterministic request record. The public record contains argument names and a digest, not raw values. Internal typed modules remain callable as programmatic components; they do not represent alternate CLI ingress paths.

## Source identity and validation evidence

`distribution/source-identity.json` covers the approved source graph. Generated repository-validation output is deliberately excluded because rerunning validation rewrites that evidence. The exact report is copied to `dist/repository-validation.json` and bound by `dist/distribution-manifest.json`. This separates immutable source identity from mutable-but-byte-accountable release evidence and prevents self-invalidating builds.
