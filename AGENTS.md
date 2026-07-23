# Agent Operating Contract

1. Read `SPECIFICATION.md`, `ARCHITECTURE.md`, and `L9_META.yaml` before editing.
2. Preserve the permanent boundary: SDK produces; Harness exercises and preserves; Assurance decides; CI Core publishes.
3. Never import Assurance implementation internals or SDK private modules.
4. Never add verdict, waiver, control, policy, GitHub publication, repository mutation, or candidate-promotion behavior.
5. Preserve canonical observation and Assurance output bytes exactly.
6. Use argv arrays with `shell=False`; confine all paths; deny ambient secrets.
7. Add tests for every public behavior and adversarial boundary.
8. Mark upstream unknowns as blocked. Never manufacture release identities or validation results.
9. Run the complete validation ladder before claiming merge readiness.
10. Do not commit, push, publish, or release without explicit authorization.
