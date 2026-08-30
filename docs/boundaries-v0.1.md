# Harness boundaries in constellation v0.1

## The harness is not an assurance authority

`l9_harness/assurance/` is not a second verdict engine and must not become one.
It is a subprocess adapter: it shells out to the real assurance CLI
(`evidence admit`, `evaluate`, `simulate`), captures stdout and stderr digests,
and stamps `"authoritative": false` on every invocation record it writes.

That posture is enforced, not merely documented:

- `assurance/cli_adapter.py` and `assurance/simulation.py` set
  `authoritative: False` on every record.
- `fallback/producer_identity.py` refuses the `l9-ci-sdk` identity and carries
  `authoritative: False`.
- `fallback/restrictions.py::assert_diagnostic_only` raises if an authoritative
  or complete Release-zero path is attempted from the fallback lane.
- `tests/contract/`, `tests/unit/`, and `tests/architecture/` assert the flag on
  the CLI's JSON output, on guidance output, and on the fallback producer.

What the harness may do: run checks in isolation, capture observations and
subprocess evidence, and invoke the assurance CLI. What it may not do: issue a
verdict, or present its own output as an admission.

## The SDK capability manifest is inactive in v0.1

`contracts/sdk.py::validate_sdk_authority` requires `id`, `version`,
`buildDigest`, `acceptedBuildDigests`, `authorizedChecks`,
`publicContractDigest`, and `producerAuthorization: "approved"`.

**`l9-ci-sdk` emits no such document.** None of those authority keys exist
anywhere in the SDK; its `RepositoryCapabilities` is an unrelated detection
result describing languages and package managers. The only instance of the
manifest is `fixtures/sdk/development/capability-manifest.json`, authored here,
carrying placeholder digests and `producerAuthorization: "pending"` — which
this repository's own validator rejects in production mode.

So the fixture is exactly what it says on the path: development-only. It is not
evidence that a producer exists, and it must not be cited as one. This is the
practical face of `UNKNOWN-005`, which already records that the approved SDK
version, build digests, check versions, and revocation policy are unavailable.

The validation code stays: it is correct, and it is what a real manifest would
be checked against. Only the implication that the manifest arrives from the SDK
today is withdrawn.

### Closing this

Either `l9-ci-sdk` specifies and publishes the capability manifest as a real
output — resolving `UNKNOWN-005` with a joint authorization record — or this
consumer is retargeted onto something the SDK actually publishes
(`l9.finding-bundle/v1`, `l9.observation`, `l9.gate-result/v1`,
`l9.agent-review-projection/v1`). A self-authored fixture is not a producer.
