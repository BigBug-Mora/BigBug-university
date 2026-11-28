# Phase 5 · Structured search and navigation

Let signed-in buyers filter published houses, apartments, and land using structured criteria, distinguish confirmed, false, and unknown vehicle access, evaluate per-area land prices by their calculated total, and restore the exact query and results when returning from a listing via **Back to Search**. [Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md) · [Phase 4 handoff](../phase-04/phase4.md#downstream-handoff)

## Progress and order

- [x] [5.1 · Property structured search endpoint](phase5.1.md). Add `GET /published-listings` behind `require_frontend_actor`, querying `property.public_listings` with tri-state vehicle access filtering, calculated total-price range filtering, area-unit normalization, and `Cache-Control: no-store`.
- [x] [5.2 · Search fixtures and PostgreSQL integration tests](phase5.2.md). Verify published fixtures for confirmed, false, and unknown vehicle access plus `per_unit` land pricing in `project/services/property/tests/test_search.py`, keeping private details and unpublished drafts excluded.
- [x] [5.3 · Buyer Search UI and Back-to-Search restoration](phase5.3.md). Build `/buyer/search` in `project/frontend/` styled per [UI design](../../mvp/containers/frontend/ui.md), preserve search params across sign-in redirects, and restore the prior query and results on **Back to Search** from `/buyer/listings/[listingId]`.
- [x] [5.4 · CI and end-to-end search acceptance](phase5.4.md). Add `project/frontend/tests/search-stack.spec.ts` to verify filtering, calculated land totals, tri-state vehicle access, and Back-to-Search navigation across the full local Compose stack and CI.

## Scope and ownership

| Owner | Deliverable |
| --- | --- |
| Property | Owns `GET /published-listings` structured search against `property.public_listings` and `property.area_units`. Enforces actor verification, tri-state `vehicle_access` matching, total-price comparison (including `per_unit` conversions), area-unit normalization, and non-cacheable responses. |
| Frontend | Owns `/buyer/search` filter controls, result cards, URL-backed query state, `returnDestination` query preservation, and **Back to Search** link wiring on `/buyer/listings/[listingId]`. |
| CI / Tests | Adds Property search integration tests (`test_search.py`) and full-stack Playwright browser tests (`search-stack.spec.ts`) executed by `identity_acceptance.py` and `.github/workflows/ci.yml`. |

Use the existing PostgreSQL 17 `property.public_listings` view (`0001_initial_schema.sql`), Phase 2 actor verification, and Phase 4 published listing page. Natural-language query parsing by the Buyer Agent belongs to Phase 11, real S3 photo thumbnails in search cards belong to Phase 06, and Property Chat belongs to Phase 12.

[Buyer search design](../../mvp/containers/agent-api/buyer-agent.md#search-mode) · [Property service spec](../../mvp/containers/property-service/property-service.md) · [Public search schema](../../mvp/database/schema.md#6-publication-and-public-search) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md)

## Phase acceptance

1. Signed-in buyers can filter published listings on `/buyer/search` by property type, district/town, price range (in the listing's currency), minimum bedrooms/bathrooms, minimum land/floor area, and vehicle access.
2. Search results and filters distinguish `vehicle_access = true` (confirmed), `vehicle_access = false` (no vehicle access), and `vehicle_access IS NULL` (unknown — marked as needing confirmation when vehicle access is requested).
3. A `land` listing priced `per_unit` (e.g., per perch) is evaluated against min/max budget filters using its `total_asking_price` calculated by `property.public_listings`, and displays both the entered per-unit price and the calculated total (with an approximate indicator when derived from an approximate land area).
4. Opening a published listing from search and clicking **Back to Search** restores the buyer's previous query parameters, filter controls, and matching results.
5. Unpublished drafts and private details (`phone`, `written_address`, `map_pin`) never appear in search responses, unauthenticated requests are rejected/redirected to sign-in with query params preserved, and all unit, integration, static, and Playwright Compose checks pass locally and in CI.

## Decisions and open questions

- **Tri-state vehicle-access filter contract:** Support `vehicle_access` modes `any` (default — returns confirmed, no, and unknown with explicit status badges), `required` (returns `true` as `matched` and `NULL` as `needs_confirmation`, excluding `false`, aligning with [Buyer Agent search](../../mvp/containers/agent-api/buyer-agent.md#search-mode) and Phase 11), `confirmed` (strictly `vehicle_access IS TRUE`), and `none` (strictly `vehicle_access IS FALSE`). Return `vehicle_access_status` (`confirmed` | `false` | `unknown`) and `match_status` (`matched` | `needs_confirmation`) per result item.
- **Price range currency handling:** `property.public_listings.total_asking_price` is stored in each listing's `currency`. When `min_price` or `max_price` is supplied alongside `currency`, filter both; when `currency` is omitted alongside a price bound, either filter by `total_asking_price` with a clear default currency (`LKR`) or match numeric `total_asking_price` while returning each listing's `currency` explicitly in the UI. Require `currency` (defaulting the UI filter currency to `LKR` when a price bound is entered) so multi-currency comparisons are never silently conflated.
- **Back-to-Search state restoration:** Store active criteria in URL query parameters on `/buyer/search`, pass that allowlisted query string as one encoded `search` parameter on `/buyer/listings/[listingId]?search=...`, and reconstruct the relative **Back to Search** destination. Preserve that context through sign-in; reject unsupported/duplicate keys, controls and oversized values. The earlier `?from=...` example was inconsistent with the explicit Phase 5.3 contract; `search` is the sole supported context parameter. Returning reruns the same filters against current published records with no-store responses.
- **Phase 2 compatibility on `/buyer/search`:** Keep `<h1>Buyer search</h1>` and render the signed-in `actor.accountId` on `/buyer/search` (and preserve `ESTATEFLOW_TEST_STANDALONE_FIXTURES=1` graceful fallback when `property-service` is absent) so Phase 2's `sign-in.spec.ts` and `identity-stack.spec.ts` continue to pass unchanged.

## Downstream handoff

Phase 6 attaches verified cover photo URLs (`gallery_photos[0]`) to search cards while preserving the no-photo card fallback. Phase 11 (Buyer Agent search) parses natural-language buyer queries into these same `GET /published-listings` structured filters and uses the `needs_confirmation` status for unknown criteria. Phase 12 links Property Chat from the listing detail page while keeping **Back to Search** intact.

## Completion evidence

Completed **2026-11-28 (Asia/Colombo)**. Final implementation SHA: **`0b60d0664394d0e3a8790d693af858e1d7960507`**; verified CI evidence head: **`244642187167bec34ef99ae13f79246ce736963d`**. [Final subphase CI passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46144370095). [Exact commands and detailed observations](phase5.4.md#evidence).

`python project/tests/integration/identity_acceptance.py` passed frontend lint/build/typecheck, **37 scoped PostgreSQL 17 Property tests**, **9 Engagement tests**, **14 standalone checks** (11 unchanged OIDC + 3 navigation/price checks), and **7 Compose browser tests**. The full workflow proved calculated land-price budget filtering, exact cross-unit comparisons, confirmed/false/unknown access behavior, private/draft isolation, sign-in resume, Back-to-Search filter/result/pagination restoration, no-store responses and desktop/mobile layouts without overflow. No migration or runtime-grant expansion was needed. Original Phase 1 SQL seeds/assertions and Phase 2 sign-in/identity test files remain unchanged.

| Subphase | Implementation / evidence commits | Property / Engagement / standalone / stack counts | CI |
| --- | --- | --- | --- |
| 5.1 | `4f26793` / `0dbd828` | 28 / 9 / 11 / 5 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46141489016) |
| 5.2 | `e114ae7` / `5b60491` | 37 / 9 / 11 / 5 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46142226695) |
| 5.3 | `732a110` / `0913b60` | 37 / 9 / 14 / 6 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46143424358) |
| 5.4 | `0b60d06` / `2446421` | 37 / 9 / 14 / 7 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46144370095) |

Planning setup `f8db20a` was pushed first. Subphases were implemented strictly in order, with each implementation/evidence push and CI success verified before the next began.
