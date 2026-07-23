# ADR-010: Unified Distribution Identity

## Status

Accepted for Harness 2.0.2.

## Decision

The approved source graph, wheel, source distribution, schema bundle, fixture bundle, CLI snapshot, SBOM, and provenance record are bound by one deterministic source identity and one distribution manifest.

The source identity excludes only itself and the generated tracked-file index to avoid recursive hashing. It is embedded byte-for-byte in the wheel, included in the source distribution, and referenced by every release manifest.

## Consequences

- A wheel cannot be represented as aligned merely because it imports.
- The wheel runtime and packaged resources must match source bytes exactly.
- The source distribution must match the approved source tree exactly.
- Wheel `RECORD` hashes must verify.
- Distribution artifacts must share the same source-tree digest.
- Build outputs remain outside the source-tree digest and are bound by the distribution manifest.
