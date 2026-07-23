# L9 Harness v2 Roadmap

## Completed in this build

- controlled clean-rewrite repository;
- strict schema-first contracts;
- subject and toolchain locking primitives;
- bounded plan resolution;
- process and container adapters;
- SDK public-contract adapter;
- exact observation preservation and indexing;
- Assurance input export and closed admission/evaluation lifecycle;
- deterministic bundles, replay, and conformance;
- diagnostic-only fallback;
- central filesystem corpus adapter with separate cache/outbox;
- deterministic Claude/Cursor guidance;
- CLI, tests, workflows, runbooks, release scripts, and provenance index.

## External gates before production integration

1. restore and pin the authoritative `l9-harness` repository baseline;
2. publish immutable Assurance 2.0.0 release tuple;
3. register and publish `l9.assurance-plan@1.0.0`;
4. approve trusted SDK version/build/check ranges;
5. publish canonicalization vectors;
6. execute producer and consumer conformance across real repositories;
7. run local-versus-hosted shadow parity;
8. obtain final architecture GO.
