# Phase 4.1 · Property showcase store, preview, and publication transaction

Extend `estateflow_property` runtime privileges, implement authored showcase persistence and seller preview reads, and build the atomic, idempotent `Publish` transaction in `project/services/property/`.

[Phase 4](phase4.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Schema](../../mvp/database/schema.md) · [Listing revisions and publication](../../mvp/database/contracts.md#listing-revisions-and-publication) · [Which value a buyer sees](../../mvp/database/contracts.md#which-value-a-buyer-sees)

## Progress

- [ ] Update `infra/aws/grant-property-runtime.sql` so `estateflow_property` can read/write `property.listings.current_showcase_id`, `property.showcase_revisions`, `property.publications`, `property.current_publications`, `property.buyer_visible_facts`, and read `property.public_listings`, `property.area_units`, `property.fact_definitions`, `property.showcase_photos`, and `property.showcase_featured_photos` with zero DDL or cross-schema grants.
- [ ] Support `approved_for_public` on versioned facts (`access_road_width`) during draft revision creation/saving (`property.revision_facts.approved_by` / `approved_at`) while preserving Phase 3 draft behavior when omitted.
- [ ] Add `project/services/property/publication.py` and Pydantic models for:
  - `POST /listings/{listing_id}/showcases` — seller-owned, idempotent by `(listing_id, action_id)`, validates non-empty `headline` / `description` / `highlights`, checks `source_revision_id == current_draft_revision_id`, writes `property.showcase_revisions` (`source_job_id = NULL`), and updates `property.listings.current_showcase_id`.
  - `GET /listings/{listing_id}/showcase` — seller-owned preview state returning the current draft revision, facts, current showcase (plus `showcase_matches_draft` boolean), active publication summary, and publication readiness (`missing_requirements`).
  - `POST /listings/{listing_id}/publish` — locks the owned listing (`FOR UPDATE`), checks idempotent replay by `(listing_id, action_id)`, enforces matching `(listing_revision_id, showcase_id)` against `current_draft_revision_id` and `current_showcase_id` (`409` on mismatch/stale), validates minimum fields by property type + 1–3 active private phone numbers (`422` if incomplete), reconciles `property.buyer_visible_facts` per `contracts.md`, inserts `property.publications`, and upserts `property.current_publications`.
- [ ] Include publication status (`published_revision_no`, `published_at`) in `GET /listings` so the seller workspace lists published vs draft status cleanly.
- [ ] Verify minimum-field validation, stale-pair rejection, idempotent replay, and `estateflow_property` privileges against disposable PostgreSQL 17.

## Acceptance check

Run the Property service unit/integration suite against disposable PostgreSQL 17 using the scoped `estateflow_property` login.

| Scenario | Expected result |
| --- | --- |
| Save authored showcase for current draft | Inserts `property.showcase_revisions` (`source_job_id IS NULL`), updates `current_showcase_id`, and replays cleanly on duplicate `action_id`. |
| Save showcase for non-current revision | Returns `409 Conflict` without overwriting `current_showcase_id`. |
| Publish with missing required fields or zero active phones | Returns `422 Unprocessable Entity` listing the missing requirements; leaves `current_publications` unchanged. |
| Publish matching `(revision, showcase)` pair | Inserts `property.publications`, sets `property.current_publications`, updates `buyer_visible_facts` for `approved_for_public` facts, and replays idempotently on duplicate `action_id`. |
| Publish stale or mismatched `(revision, showcase)` pair | Returns `409 Conflict` and preserves the prior publication. |
