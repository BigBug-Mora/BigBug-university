# Phase 5.4 · CI and end-to-end search acceptance

Verify the complete Phase 5 structured search and Back-to-Search workflow across authenticated seller and buyer sessions in Docker Compose and confirm GitHub Actions CI passes.

[Phase 5](phase5.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 4.4 reference](../phase-04/phase4.4.md)

## Progress

- [ ] Add `project/frontend/tests/search-stack.spec.ts` running against the full local Compose stack (`frontend` + `property-service` + `engagement-service` + PostgreSQL 17 + `identity-fixture`):
  - Seller API/UI publishes representative listings distinguishing:
    1. `land` with `per_unit` pricing (`250000 LKR / perch`, `0.125 acre` = `5,000,000 LKR` calculated total, `land_area_approximate = true`) and `vehicle_access = true` (confirmed).
    2. `house` with `vehicle_access = false` (explicitly no vehicle access), `bedroom_count = 0`, `parking_spaces = 0`.
    3. `apartment` (or `land`) with `vehicle_access = null` (unknown).
    4. An unpublished draft listing (must never appear in search).
  - Unauthenticated buyer navigating directly to `/buyer/search?property_type=land&vehicle_access=required` is redirected to `/sign-in` and resumes `/buyer/search?property_type=land&vehicle_access=required` after sign-in.
  - Signed-in buyer filters by vehicle access (`any`, `required`, `confirmed`, `none`), confirming `confirmed` vs `unknown` (`needs confirmation`) vs `false` behavior.
  - Buyer filters land by `max_price` (e.g., `5500000` includes the `250000/perch` plot and shows its approximate calculated total; `4500000` excludes it) and by cross-unit area (`min_land_area=15&land_area_unit=perch`).
  - Buyer opens a listing from the filtered results, verifies the published listing page, clicks **Back to Search**, and confirms the previous filters, URL query string, and matching result cards are restored.
  - Verify `Cache-Control: no-store`, zero private phone numbers in search responses/DOM, and desktop + mobile (`390×844`) responsive layout without horizontal overflow.
- [ ] Run the full local acceptance suite (`python project/tests/integration/identity_acceptance.py`) and verify GitHub Actions CI passes.
- [ ] Record exact commands, Git revision, date, and observed results in **Evidence** below before ticking Phase 5 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts disposable PostgreSQL 17 and the Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Engagement tests, Frontend static checks, standalone sign-in tests, and Compose browser tests (including `search-stack.spec.ts`) pass.
3. GitHub Actions CI passes on the Phase 5 commits.

## Evidence

*(To be recorded after verification runs.)*
