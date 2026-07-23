# Contributing

Changes must be narrow, schema-first, deterministic, and boundary-preserving.

Required sequence:

1. identify the owning repository and contract;
2. update schemas and fixtures together;
3. regenerate bindings;
4. implement the smallest complete change;
5. add unit, contract, integration, architecture, and adversarial tests as applicable;
6. run the validation ladder;
7. update traceability, changelog, and migration/provenance records.

Protocol or trust changes require architecture and security review. No PR may introduce verdict logic, GitHub publication, repository mutation, SDK identity impersonation, proprietary Assurance envelopes, or automatic candidate promotion.
