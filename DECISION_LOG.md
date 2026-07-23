# Decision Log

## DL-001: Separate source identity from mutable validation evidence

**Decision:** `docs/validation/repository-validation.json` is excluded from the immutable source-tree digest and copied into `dist/` as separately hashed release evidence.

**Reason:** Running repository validation rewrites its report. Including that report in the source digest created a self-invalidating release cycle.

## DL-002: One CLI ingress, composable internal modules

**Decision:** Every CLI command is normalized and validated through `l9_harness.application.ingress` before dispatch. Typed programmatic modules remain directly composable for tests and embedding.

**Reason:** This provides one ingress and one trace assignment without converting Harness into a workflow engine or breaking its internal API.

## DL-003: One canonical file tree

**Decision:** Replace `FINAL_TREE.md` and `FINAL_REPO_TREE.md` with `FILETREE.md`.

**Reason:** The two files differed only by title and duplicated active inventory responsibility.

## DL-004: Bind validation evidence at distribution level

**Decision:** The wheel/sdist release includes a byte-preserved copy of the repository-validation report and records its digest in the distribution manifest.

**Reason:** Mutable evidence should be independently verifiable without contaminating the immutable source identity.

## D-009: Canonical source inventory is singular and enforced

**Decision:** `FILETREE.md` is the only source-tree inventory artifact. `FINAL_TREE.md` and `FINAL_REPO_TREE.md` are prohibited from source distributions and release packs.

**Reason:** Duplicate inventories drifted from the generator and broke the pack's own source-identity and test contracts.

## D-010: Wheel and sdist metadata are public regression contracts

**Decision:** Package name, version, Python requirement, summary, and canonical tree membership are validated from freshly built artifacts.

**Reason:** Source tests alone do not prove the wheel and sdist expose the intended public release identity.

