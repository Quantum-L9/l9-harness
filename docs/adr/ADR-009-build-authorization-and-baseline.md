# ADR-009: Build Authorization and Unavailable Baseline

## Status

Accepted for this generated build.

## Decision

Build the complete Harness v2 clean-rewrite repository from the locked v1.2.1 specification because the target GitHub repository could not be retrieved. Preserve `UNKNOWN_REPOSITORY_UNAVAILABLE` as the source baseline identity and prohibit claims of live-repository compatibility until Phase 0 is rerun against an accessible immutable commit.

## Consequences

- Harness-owned behavior can be implemented and validated locally.
- Production cross-repository adapters remain fail-closed.
- No remote mutation is implied or authorized.
- A later baseline reconciliation may require a controlled merge or asset-disposition pass.
