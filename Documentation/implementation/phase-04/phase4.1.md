# Phase 4.1 · Property showcase store, preview, and publication transaction

Extend `estateflow_property` runtime privileges, implement authored showcase persistence and seller preview reads, and build the atomic, idempotent `Publish` transaction in `project/services/property/`.

[Phase 4](phase4.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Schema](../../mvp/database/schema.md) · [Listing revisions and publication](../../mvp/database/contracts.md#listing-revisions-and-publication) · [Which value a buyer sees](../../mvp/database/contracts.md#which-value-a-buyer-sees)

## Progress

- [x] Update `infra/aws/grant-property-runtime.sql` so `estateflow_property` can read/write `property.listings.current_showcase_id`, `property.showcase_revisions`, `property.publications`, `property.current_publications`, `property.buyer_visible_facts`, and read `property.public_listings`, `property.area_units`, `property.fact_definitions`, `property.showcase_photos`, and `property.showcase_featured_photos` with zero DDL or cross-schema grants.
- [x] Support `approved_for_public` on versioned facts (`access_road_width`) during draft revision creation/saving (`property.revision_facts.approved_by` / `approved_at`) while preserving Phase 3 draft behavior when omitted.
- [x] Add `project/services/property/publication.py` and Pydantic models for:
  - `POST /listings/{listing_id}/showcases` — seller-owned, idempotent by `(listing_id, action_id)`, validates non-empty `headline` / `description` / `highlights`, checks `source_revision_id == current_draft_revision_id`, writes `property.showcase_revisions` (`source_job_id = NULL`), and updates `property.listings.current_showcase_id`.
  - `GET /listings/{listing_id}/showcase` — seller-owned preview state returning the current draft revision, facts, current showcase (plus `showcase_matches_draft` boolean), active publication summary, and publication readiness (`missing_requirements`).
  - `POST /listings/{listing_id}/publish` — locks the owned listing (`FOR UPDATE`), checks idempotent replay by `(listing_id, action_id)`, enforces matching `(listing_revision_id, showcase_id)` against `current_draft_revision_id` and `current_showcase_id` (`409` on mismatch/stale), validates minimum fields by property type + 1–3 active private phone numbers (`422` if incomplete), reconciles `property.buyer_visible_facts` per `contracts.md`, inserts `property.publications`, and upserts `property.current_publications`.
- [x] Include publication status (`published_revision_no`, `published_at`) in `GET /listings` so the seller workspace lists published vs draft status cleanly.
- [x] Verify minimum-field validation, stale-pair rejection, idempotent replay, and `estateflow_property` privileges against disposable PostgreSQL 17.

## Acceptance check

Run the Property service unit/integration suite against disposable PostgreSQL 17 using the scoped `estateflow_property` login.

| Scenario | Expected result |
| --- | --- |
| Save authored showcase for current draft | Inserts `property.showcase_revisions` (`source_job_id IS NULL`), updates `current_showcase_id`, and replays cleanly on duplicate `action_id`. |
| Save showcase for non-current revision | Returns `409 Conflict` without overwriting `current_showcase_id`. |
| Publish with missing required fields or zero active phones | Returns `422 Unprocessable Entity` listing the missing requirements; leaves `current_publications` unchanged. |
| Publish matching `(revision, showcase)` pair | Inserts `property.publications`, sets `property.current_publications`, updates `buyer_visible_facts` for `approved_for_public` facts, and replays idempotently on duplicate `action_id`. |
| Publish stale or mismatched `(revision, showcase)` pair | Returns `409 Conflict` and preserves the prior publication. |

## Implementation decisions

- Publication and private-phone mutations acquire the same listing row lock. Retiring the last active phone on a live listing returns `422`; retries of already retired details remain harmless.
- Authored showcase saves use `parent_showcase_id` as an optimistic concurrency check as well as checking the source draft. Replay is checked under the listing lock before either concurrency check and never advances later pointers.
- Public approval belongs to the exact fact version. Omitted approval preserves an unchanged parent link; a new width version defaults to private unless explicitly approved. Removing a public version preserves an independently shared answer pointing at another version.
- Registered dedicated inquiry mappings are limited to `bedroom_count` and `covered_parking_spaces`. Publication compares each value and its evidence and only removes chat overrides according to the existing contract.

## Evidence

Verified 2026-11-28 (Asia/Colombo), implementation revision `e56503d3dfd3170b9bf8bfdf20786ac5aa967464`. Plan setup was committed and pushed first as `494b1bf3b19a04a5ba8369405c1f3d023a858d12` ([successful CI](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46135239928)).

Commands from the repository root in a disposable Linux copy using Ubuntu WSL Docker Engine + Compose:

```sh
npm --prefix project/frontend run lint
npm --prefix project/frontend run build
npm --prefix project/frontend run typecheck
npm --prefix project/frontend run test:e2e
python project/tests/integration/identity_acceptance.py
```

Frontend lint, production build and TypeScript passed. Standalone Playwright passed **11/11** (22.0 s), including `courtyard-house`; it ran in the cached `mcr.microsoft.com/playwright:v1.65.1-noble` image with host networking. The unchanged full acceptance runner subsequently exited **0** using native WSL Chromium after installing its shared libraries. It applied Alembic `0001 (head)`, ran **21 Property tests**, **9 Engagement tests**, and **2 Compose browser tests**, and removed its disposable stack.

The runner executes these service commands using the scoped test database URLs:

```sh
python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v
python -W error::ResourceWarning -m unittest discover -s project/services/engagement/tests -v
```

Property tests assert PostgreSQL **17**, login **estateflow_property**, and denial of DDL, cross-schema reads, immutable-publication deletion, showcase updates, and seller-identity updates. Positive author/publish/reconciliation operations pass under the same grants. Regression checks cover all three property types, zero-valued counts, missing phones, ownership, stale pairs, simultaneous replay, public approval inheritance/removal, and independently shared versioned/dedicated corrections.

Environment notes: fresh Linux npm installation stalled; dependencies were recovered from the already cached frontend Docker build stage. Initial browser attempts lacked Chromium libraries, then encountered root-owned disposable Playwright output from the container run; installing dependencies and correcting that output ownership resolved both. No application checks were weakened. An attempted Docker-socket mount into the Playwright container was rejected by automatic approval review and was not used. Remaining subphases use a persistent Linux test copy to retain logs across WSL shutdowns.
