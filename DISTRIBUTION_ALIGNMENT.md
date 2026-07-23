# Distribution Alignment Contract

Harness 2.0.4 binds its source repository, wheel, source distribution, schemas, fixtures, CLI snapshot, validation evidence, SBOM, and provenance through deterministic release records.

## Source identity

`distribution/source-identity.json` records the approved source file set, raw SHA-256 and byte length for each file, one source-tree digest, schema and fixture digests, and explicit recursive-hash exclusions. The file is embedded byte-for-byte in the wheel and included in the source distribution.

## Distribution manifest

`dist/distribution-manifest.json` binds every generated distribution artifact to the source identity and the exact repository-validation evidence. `dist/distribution-alignment.json` records executed parity checks.

## Required proof

A distribution passes only when:

1. source identity matches the approved source graph;
2. wheel runtime and resource files match source bytes;
3. wheel metadata matches the canonical project contract;
4. wheel `RECORD` hashes and sizes verify;
5. sdist contains the exact approved source files with one canonical `FILETREE.md`;
6. stale `FINAL_TREE.md` and `FINAL_REPO_TREE.md` artifacts are absent;
7. distribution artifacts have recorded raw SHA-256 digests;
8. repository-validation evidence is copied byte-for-byte and digest-bound;
9. two independent builds produce byte-identical release artifacts.

Canonical semantic equality does not replace raw-byte equality.
