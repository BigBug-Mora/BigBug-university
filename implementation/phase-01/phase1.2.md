# Phase 1.2 · Versioned database and fixtures

Create a repeatable way to build the schema described in the MVP docs and verify that it can hold representative listing data. Keep the initial migration explicit and reviewable. [Phase 1](phase1.md) · [Database diagram source](../../Documentation/mvp/database/schema.md) · [Database contracts](../../Documentation/mvp/database/contracts.md) · [Migration checks](../../Documentation/mvp/ci/cd/ci.md)

## Progress

- [ ] Coordinate with [Phase 1.4](phase1.4.md) to choose the RDS PostgreSQL major version and use it for disposable tests. Use Alembic as the default with SQLAlchemy and record the implementation choice and exact commands.
- [ ] Create one migration history under `project/migrations/`. Translate the documented DDL into the first migration, preserving schemas, keys, checks, indexes, views, and required reference data. Record any DDL discrepancy and resolve its effect before applying that migration to shared RDS.
- [ ] Add a disposable database configuration in `project/compose.test.yaml`. Keep credentials and fixture loading isolated from shared RDS. Expose separate, explicit commands for migrations and fictional fixtures.
- [ ] Add repeatable fixtures covering House, Apartment, and Land, with a draft revision, null and false facts, and a published land example with a per-area asking price. Use fictional identities and synthetic private test values if needed.
- [ ] Document the migration identity and expected runtime access by schema. Test any roles introduced in this phase and record how later phases will refine the grants they need.

## Acceptance check

Start an empty disposable PostgreSQL instance. Run the migration command, load fixtures, and run database assertions. Verify the three property types, that a draft-only listing is absent from the public view, and that the published plot has the expected total asking price and vehicle-access value. Run the migration command a second time and confirm there is no revision left to apply. Teardown is scoped to the disposable database. Hand the verified commands to Phase 1.3 before a shared migration is attempted.

## Decision log

- Store reference data required by the schema in migrations. Load fictional demonstration rows through a separate fixture command.
