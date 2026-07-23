# Security Policy

Harness processes untrusted repositories, observations, archives, logs, Markdown, and external CLI output.

## Enforced controls

- argv execution with `shell=False`;
- minimal environment allowlist and secret-like key rejection;
- path confinement and portable relative-path validation;
- symlink and traversal rejection during extraction;
- archive expanded-size limits;
- strict JSON Schemas for Harness-owned security-sensitive objects;
- exact raw digests for all preserved files;
- sanitized console/Markdown output;
- fallback producer isolation;
- no credentials, test keys, or private signers in production code;
- no hidden network access in offline profiles.

## Reporting

Use the repository security advisory channel. Do not place secrets or customer evidence in public issues. Until the authoritative repository is accessible, the disclosure endpoint is `UNKNOWN`.

## Object-store corpus boundary

Object-store corpus access is HTTPS-first. URLs with credentials or fragments are rejected, redirects are prohibited, optional host allowlists are supported, and transfers are bounded before materialization. Plain HTTP requires explicit insecure opt-in and is not suitable for production authority.

## Distribution integrity

The wheel, sdist, schemas, fixtures, CLI snapshot, SBOM, and provenance are bound to one source identity. Wheel `RECORD` validation and exact source/resource byte comparison are mandatory. A semantically equivalent but byte-rewritten decision or observation is not considered transport-preserved.
