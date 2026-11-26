# Phase 1.2 · Versioned database and fixtures

Create a repeatable way to build the schema described in the MVP docs and verify that it can hold representative listing data. Keep the initial migration explicit and reviewable. [Phase 1](phase1.md) · [Database diagram source](../../mvp/database/schema.md) · [Database contracts](../../mvp/database/contracts.md) · [Migration checks](../../mvp/ci/cd/ci.md)

## Progress

- [x] Coordinate with [Phase 1.4](phase1.4.md) on PostgreSQL 17. Use Alembic with SQLAlchemy and Psycopg. Record the exact commands for Phase 1.3.
- [x] Create one migration history under `project/migrations/`. Revision `0001` preserves the documented schemas, keys, checks, indexes implied by constraints, view, and required reference data.
- [x] Add disposable PostgreSQL in `project/compose.test.yaml` with its own loopback port, credentials, and in-memory data directory. Apply migrations and load fictional fixtures as separate commands.
- [x] Add repeatable House, Apartment, and Land fixtures covering draft visibility, unknown and false facts, and a published land listing with a per-area asking price.
- [x] Document migration ownership and expected runtime grants. Verify the disposable migration owner can apply the revision without superuser, role creation, or database creation privileges.

## Acceptance check

Start an empty disposable PostgreSQL instance. Run the migration command, load fixtures, and run database assertions. Verify the three property types, that a draft-only listing is absent from the public view, and that the published plot has the expected total asking price and vehicle-access value. Run the migration command a second time and confirm there is no revision left to apply. Teardown is scoped to the disposable database. Hand the verified commands to Phase 1.3 before a shared migration is attempted.

## Verification and CI handoff

Run the [disposable database commands](../../../README.md#verify-the-disposable-database) from the repository root. Phase 1.3 can use the same Compose and Python commands with the Bash environment variable shown there.

Verified on 2026-11-26 using PostgreSQL 17.12 and Python 3.14:

- `upgrade head` applied revision `0001` to the empty database. The migration ran under the dedicated owner. `upgrade head --sql` also generated a transactional SQL script for review.
- The fixture load passed twice. The database assertions confirmed that the two draft-only listings stayed out of the public view and that the published land listing had confirmed vehicle access and a derived asking price of LKR 5,000,000 for 0.125 acre at LKR 250,000 per perch.
- A second `upgrade head` applied no revision. `current --check-heads` reported `0001 (head)`.
- The existing Property service health test passed. `docker compose down` removed the disposable database container and its dedicated network.

## Database identities

Use a dedicated migration owner to own the EstateFlow database and its objects, including `public.alembic_version`. Give it database-level ownership without server administration privileges. The disposable database bootstraps and tests this setup with `estateflow_migrator`. Phase 1.4 owns shared identity setup, target verification, and coordination of the explicit migration command.

| Runtime identity | Expected access when introduced |
| --- | --- |
| Property | `property` schema usage and operation-specific read and write access. Reference catalogs are read-only to runtime code. Keep immutable revisions and evidence append-only. |
| Engagement | `account` and `engagement` schema usage and operation-specific read and write access. Phase 13 defines the narrow Property access required for the shared answer transaction. |
| Agent API, dispatcher, and worker | `agent` schema usage and permissions for each process's own run or job operations. Other records are resolved through the owning APIs. |
| Frontend | Calls backend APIs and needs no database access. |

Each feature phase introduces and verifies the exact grants it needs. PostgreSQL foreign keys between schemas preserve integrity without granting runtime roles direct reads of the referenced data.

## Decision log

- Store reference data required by the schema in migrations. Load fictional demonstration rows through a separate fixture command.
- Revision `0001` snapshots the MVP schema SQL as written. The PostgreSQL 17 migration revealed no DDL discrepancies. Make later changes in new revisions. The initial revision has no destructive downgrade. Restore a verified backup to roll back a shared database, or recreate the disposable database.
- PostgreSQL 17 is the target for both disposable tests and Phase 1.4. An authenticated read-only AWS check found no existing RDS for PostgreSQL instances in the configured `us-east-1` region and confirmed major 17 is offered there. Shared provisioning and migration remain Phase 1.4 work. [RDS release calendar](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-release-calendar.html)
