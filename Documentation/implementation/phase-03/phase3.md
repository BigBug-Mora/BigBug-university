# Phase 3 · Seller listing drafts

Build the seller draft editor and Property service operations so an authenticated seller can create, save, and reopen incomplete listing drafts for houses, apartments, and land, record typed facts without conflating zero or false with unknown, retry saves safely, and manage encrypted private details under stable IDs while denying other accounts. [Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md) · [Phase 2 handoff](../phase-02/phase2.md#downstream-handoff)

## Progress and order

- [x] [3.1 · Property draft store, revisions, and ownership](phase3.1.md). Provision the scoped Property runtime database login, add listing/revision persistence and typed-fact validation for houses, apartments, and land, and enforce seller ownership on all draft routes.
- [x] [3.2 · Encrypted private details](phase3.2.md). Implement authenticated encryption for `property.private_details`, slot management for phone numbers, written address, and map pin, in-place edits, and permanent ID retirement on removal.
- [ ] [3.3 · Seller draft editor in Frontend](phase3.3.md). Add the server-side Property draft client and the signed-in seller workspace/editor UI for creating, editing, and reopening drafts and private details.
- [ ] [3.4 · CI and end-to-end draft acceptance](phase3.4.md). Run cross-service and Playwright draft acceptance checks across two authenticated accounts and add the deterministic checks to CI.

## Scope and ownership

| Owner | Deliverable |
| --- | --- |
| Property | Owns `property.listings`, `property.listing_revisions`, `property.fact_versions`, `property.revision_facts`, and `property.private_details`. Enforces seller ownership via the Phase 2 actor dependency, validates typed facts and revision concurrency, handles idempotent retries, and encrypts/decrypts private details. |
| Frontend | Owns the seller workspace listing list and draft editor under `/seller/workspace` and server-side calls to Property using the signed-in user's access token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN`. |
| Shared / Migrations / CI | Uses `0001` (adding an ordered migration only if a schema gap is discovered). Adds the scoped `estateflow_property` runtime database login and integrates Phase 3 deterministic tests into `.github/workflows/`. |

Use the existing PostgreSQL 17 schema and Phase 2 identity/actor boundary. Showcase generation, preview, explicit publication, photo uploads, buyer search, and buyer disclosure grants belong to Phases 4–6 and 14.

[Property service spec](../../mvp/containers/property-service/property-service.md) · [Database schema](../../mvp/database/schema.md) · [Listing revisions contract](../../mvp/database/contracts.md#listing-revisions-and-publication) · [Standard fields and flexible facts](../../mvp/database/contracts.md#standard-fields-and-flexible-facts) · [Private disclosures contract](../../mvp/database/contracts.md#private-disclosures) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md)

## Phase acceptance

1. A signed-in seller creates and saves an incomplete draft for a house, apartment, and land listing, then reloads/reopens each draft and sees all saved fields intact.
2. Explicit `0` and `false` values (such as `bedroom_count = 0`, `parking_spaces = 0`, `covered_parking_spaces = 0`, `vehicle_access = false`) remain distinct from `NULL`/unknown, and land `per_unit` vs `total` pricing preserves the entered amount and unit.
3. Retrying a listing creation (`create_action_id`) or revision save (`edit_action_id`) preserves the intended listing and revision without creating duplicate rows or corrupting `current_draft_revision_id`.
4. Private details (1–3 distinct phone numbers, optional written address, optional map pin) are stored encrypted in `property.private_details`; editing updates in place under the same `id`, removing clears the value and retires `id`, and re-adding in the same slot creates a new `id`.
5. Unauthenticated requests and requests from a different authenticated account are denied on every draft and private-detail endpoint.
6. All Phase 3 unit, integration, and Playwright checks pass locally and in CI. Record commands, revision, and results in [3.4](phase3.4.md) before ticking Phase 3 in the roadmap.

## Decisions and open questions

- **Database schema baseline:** `0001_initial_schema.sql` already defines `property.listings`, `property.area_units`, `property.listing_revisions`, `property.fact_definitions`, `property.fact_applicability`, `property.fact_versions`, `property.revision_facts`, and `property.private_details`. Add a new Alembic migration only if implementation reveals a missing constraint or index.
- **Runtime database role:** Follow the Phase 2.1 `estateflow_engagement` pattern by introducing a scoped `estateflow_property` runtime login with minimum required privileges on `property.*` tables, separate from the migration owner.
- **Encryption key configuration:** Define a clear environment variable contract for private-detail encryption (local/CI test key vs shared/hosted key reference) in [3.2](phase3.2.md) so `encryption_key_ref` supports future key rotation.

- Revisions use complete dedicated-field snapshots. Omitting a versioned road width preserves the parent link, explicitly clearing it removes the link, and editing it creates a new immutable version. An action replay returns the original revision even after a later save.
- Every private mutation locks the owned listing, serializing phone uniqueness checks with slot edits and retirement. Fernet authenticates the detail ID and value together. The JSON key map contains URL-safe base64 Fernet keys. Keep old references configured while any active rows still use them.
- Seller routes use a uniform 404 for unavailable or foreign listings. Browser retry storage contains a submission digest and UUID. Private values are confined to the authorized private-detail flow.

## Downstream handoff

Phase 4 builds showcase preview and explicit publication on top of `property.listing_revisions` and `property.listings.current_draft_revision_id`. Phase 6 attaches verified S3 photos to draft revisions. Phase 10 connects Seller Agent onboarding to the same draft and typed-fact operations. Phase 13 and Phase 14 build inquiry answer sharing and buyer disclosure grants against `property.revision_facts` and `property.private_details`.
