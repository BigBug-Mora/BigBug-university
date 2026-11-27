# Phase 3.1 · Property draft store, revisions, and ownership

Add PostgreSQL persistence to the Property service, provision its scoped runtime database login, and implement seller-owned listing draft creation, reading, and revision saving for houses, apartments, and land.

[Phase 3](phase3.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Schema](../../mvp/database/schema.md) · [Listing revisions](../../mvp/database/contracts.md#listing-revisions-and-publication) · [Standard fields and flexible facts](../../mvp/database/contracts.md#standard-fields-and-flexible-facts)

## Progress

- [x] Reuse `0001` (`property.listings`, `property.area_units`, `property.listing_revisions`, `property.fact_definitions`, `property.fact_applicability`, `property.fact_versions`, `property.revision_facts`). Add reviewed SQL and runbook updates for a scoped `estateflow_property` runtime login with minimum `SELECT`/`INSERT`/`UPDATE` grants on `property` tables as needed (no DDL). Exercise those grants against disposable PostgreSQL 17.
- [x] Add Property database configuration (`ESTATEFLOW_PROPERTY_DATABASE_URL`), connection/transaction helpers, and repository modules under `project/services/property/` (keeping HTTP routing, domain validation, and SQL queries cleanly separated).
- [x] Implement seller draft endpoints behind `require_frontend_actor`:
  - `POST /listings` — idempotent by `(seller_account_id, create_action_id)`; creates `property.listings` and initial `revision_no = 1` in one transaction, setting `current_draft_revision_id`.
  - `GET /listings` — lists drafts owned by `actor.account_id`.
  - `GET /listings/{listing_id}` — returns the listing and its current draft revision (and versioned facts linked via `property.revision_facts`), denying any account where `seller_account_id != actor.account_id`.
  - `POST /listings/{listing_id}/revisions` — locks the listing row, checks `seller_account_id == actor.account_id`, handles idempotent replay by `(listing_id, edit_action_id)`, validates `parent_revision_id` against `current_draft_revision_id` (returning `409 Conflict` on stale concurrent edits), inserts `revision_no + 1`, copies/updates `property.revision_facts` (and new `property.fact_versions` when versioned facts like `access_road_width` change), and advances `current_draft_revision_id`.
- [x] Enforce property-type rules and `0`/`false` vs `NULL`/unknown preservation:
  - Support `house`, `apartment`, and `land` with all dedicated columns and SQL check invariants (e.g., `land` disallows house/apartment fields; `floor_area_unit` restricted to `sq_ft`/`sq_m`; `price_basis = 'per_unit'` restricted to `land` with `price_area_unit`; `covered_parking_spaces <= parking_spaces`; `attached_bathroom_count <= bathroom_count`; `ground_floor_bedrooms <= bedroom_count`).
  - Preserve explicit `0` and `false` values separately from `NULL`/unknown, and store `approximate`, `source_kind`, and `qualifier` in `standard_fact_evidence` or `property.fact_versions`.
- [x] Update `project/services/property/Dockerfile` and `project/compose*.yaml` if needed so Property connects to PostgreSQL in container builds.
- [x] Add PostgreSQL integration tests under `project/services/property/tests/` covering all three property types, `0`/`false` vs `unknown`, idempotent retries, stale-parent conflicts, and cross-account denial.

## Acceptance check

Start `project/compose.test.yaml`, apply Alembic to head, and provision `estateflow_property`. Run the Property integration suite against disposable PostgreSQL through `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Create and reopen house, apartment, and land drafts | Saved fields, units, `approximate` flags, and `standard_fact_evidence` round-trip accurately; incomplete drafts succeed. |
| Explicit `0` and `false` vs `NULL`/unknown | `0` bedrooms/parking and `vehicle_access = false` are returned as `0`/`false`, while omitted fields remain `null`. |
| Retry `create_action_id` or `edit_action_id` | Returns the original listing/revision without creating duplicates or advancing `revision_no` twice. |
| Stale `parent_revision_id` | Returns `409` without overwriting the newer draft. |
| Different authenticated account or unauthenticated caller | Returns `401` (unauthenticated) or `403`/`404` (different seller) with no data leaked. |
| Runtime login probe | `estateflow_property` can read/write `property.*` draft tables and is denied DDL or `account.*`/`engagement.*` access. |
