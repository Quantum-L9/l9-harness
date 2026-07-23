# L9 Harness Recursive Improvement Report

## Decision

```yaml
recursive_improvement: PASS
architecture_alignment: PASS
assurance_boundary_alignment: PASS
release_zero_check_alignment: PASS
canonical_pack_structure: PASS
wheel_and_sdist_contract_alignment: PASS
transport_packet_applicability: PASS_WITH_EXPLICIT_NOT_APPLICABLE_BOUNDARIES
packet_envelope_status: PROHIBITED
l9_metadata_coverage: PASS_BY_REPOSITORY_META_AND_PER_FILE_INDEX
production_assurance_adapter: BLOCKED_BY_EXTERNAL_AUTHORITY
production_sdk_adapter: BLOCKED_BY_EXTERNAL_AUTHORITY
authoritative_ci_dependency_on_harness: PROHIBITED
```

## Improvement conclusion

The repository was improved, not re-architected. The pass removed stale source-pack artifacts, strengthened release validation, normalized operational evidence, and preserved all established ownership and public interfaces.

## Preserved boundary

```text
CI Core orchestrates and publishes.
CI SDK executes checks and emits canonical observations.
Harness coordinates local execution, preserves bytes, exercises conformance, and replays.
Assurance admits evidence, evaluates controls, and issues decisions.
```

## Recursive passes

1. Extract: repository, wheel, sdist, schemas, reports, public CLI, and release identity inventoried.
2. Classify: runtime, contracts, schemas, tests, validation tools, evidence, and generated artifacts mapped.
3. Audit: stale duplicate inventories and missing distribution-level regression assertions confirmed.
4. Strengthen: canonical inventory ownership became a repository gate.
5. Deduplicate: `FINAL_TREE.md` and `FINAL_REPO_TREE.md` removed.
6. Normalize: all active release and evidence records updated to 2.0.4.
7. Clarify: the source-to-wheel-to-sdist contract is explicit in tests and reports.
8. Enforce: wheel metadata, sdist membership, and CLI version tests added.
9. Validate: 82 tests, 27 repository gates, and eight generated artifacts pass.
10. Converge: independent builds and installed-wheel verification produce no material residual Harness-owned defect.

## L9 applicability

Harness is CI tooling, not a runtime node. Gate-only node egress is not applied to local filesystem artifact exchange or explicit external CLI invocation. `PacketEnvelope` remains prohibited. `TransportPacket` remains an SDK-owned repository check and is not redefined as a Harness-to-Assurance envelope.

## Remaining external unknowns

- live immutable Harness repository baseline;
- repository license and distribution authorization;
- immutable Assurance production release tuple;
- registered production Assurance plan schema and canonicalization vectors;
- trusted SDK production tuple;
- CI Core hosted shadow-parity evidence;
- local Ruff and mypy results.

None of these unknowns is converted into a passing production claim.
