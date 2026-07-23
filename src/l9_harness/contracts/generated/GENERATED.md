# Generated Contract Bindings

Harness-owned JSON Schemas are authoritative.

`scripts/generate_bindings.py` deterministically produces:

- `schema_inventory.py`, the canonical schema ID inventory;
- `models.py`, schema-derived `TypedDict` document surfaces preserving required and optional fields.

`scripts/verify_generated.py` fails when committed generated files drift from the schemas. Assurance-owned schemas are never copied without an immutable upstream source and provenance record.
