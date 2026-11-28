# Phase 5.3 · Buyer Search UI and Back-to-Search restoration

Build the signed-in `/buyer/search` screen in `project/frontend/` and wire **Back to Search** navigation on `/buyer/listings/[listingId]` so returning from a listing restores the buyer's previous query and results.

[Phase 5](phase5.md) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md)

## Progress

- [x] Extend `project/frontend/src/server/property.ts` with `searchPublishedListings(params)` calling `GET /published-listings?...` using the signed-in user's access token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN` (never exposing tokens to client components).
- [x] Update `project/frontend/src/server/destinations.ts`:
  - Allow `returnDestination` to preserve valid query parameters on `/buyer/search?...` (and validated `/buyer/listings/{uuid}?search=...` return context) across Cognito sign-in redirects without permitting open redirects or invalid paths.
- [x] Build the `/buyer/search` page (`project/frontend/src/app/buyer/search/page.tsx` and modular client filter/result components):
  - Keep `<h1>Buyer search</h1>` and show `actor.accountId` (plus graceful standalone fixture fallback when `ESTATEFLOW_TEST_STANDALONE_FIXTURES=1` and `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER=1`), preserving Phase 2 `sign-in.spec.ts` and `identity-stack.spec.ts` assertions.
  - Follow [UI design](../../mvp/containers/frontend/ui.md): tighter search spacing, consistent card proportions, predictable placement of headline, location (`Town, District`), formatted price (`entered_price` + calculated total & `"Approximate total"` badge for `per_unit` land), key facts (`Land area`, `Floor area`, `Bedrooms`, `Bathrooms`), and explicit vehicle-access badges (`Confirmed`, `No vehicle access`, `Unknown — needs confirmation`).
  - Provide structured filter controls (`property_type`, `district`, `town`, `currency`, `min_price`, `max_price`, `min_bedrooms`, `min_bathrooms`, `min_land_area` + `land_area_unit`, `vehicle_access`: `Any` / `Required (include unknown)` / `Confirmed only` / `No vehicle access`, plus `Clear filters`) synced via URL query parameters (`GET` navigation / `router.push`).
- [x] Wire **Back to Search** on `project/frontend/src/app/buyer/listings/[listingId]/page.tsx`:
  - Search result cards link to `/buyer/listings/${id}?search=${encodeURIComponent(currentQuery)}` (only when `currentQuery` is non-empty).
  - `/buyer/listings/[listingId]` validates the `search` query param safely (stripping any non-search/unsafe characters, reconstructing `/buyer/search?...`) and renders `<Link href={backToSearchHref}>Back to Search</Link>` so clicking **Back to Search** restores the exact prior filters and results.
- [x] Verify `npm --prefix project/frontend run lint`, `typecheck`, `build`, and standalone `test:e2e` pass with zero warnings/errors.

## Acceptance check

Verify frontend static checks and interactive search + navigation behavior against the local stack.

| Scenario | Expected result |
| --- | --- |
| `lint`, `typecheck`, `build`, standalone `test:e2e` | All pass cleanly with zero warnings or errors; `sign-in.spec.ts` passes unchanged. |
| Filter controls & result cards | Cards consistently show price (with calculated land total when `per_unit`), location, key measurements, and vehicle-access status badges. |
| Unknown vehicle access under `required` | Appears with an explicit `"Needs confirmation"` / `"Unknown"` badge after confirmed matches. |
| **Back to Search** navigation | Navigating from filtered search to a listing and clicking **Back to Search** restores the query URL, form values, and matching result set. |

## Contract decisions

- `src/lib/search-navigation.ts` owns navigation safety and browser-form transport only: allowlisted keys, no duplicates/control characters/fragments, bounded lengths, UUID listing links, and one encoded `search` query-string token. Property continues to validate filter semantics. Unknown/unsafe context falls back to `/buyer/search`; arbitrary destinations are never used as link targets. The main plan's old `?from=...` example was corrected to the explicit `?search=...` contract.
- GET forms retain URL state, remove blank inputs and inactive default unit selections before calling Property, and default a missing currency to LKR only when a price bound is present. New filter submissions reset pagination. Clear filters also resets local unsent fields. Pagination and Back to Search retain the query string; returning reruns the same criteria with no-store rather than serving cached listing data.
- Search cards use no-photo typographic headers, explicit tri-state access badges and existing measurement/provenance formatting. Decimal-string prices are grouped using integer cents so values near the schema's numeric limit retain cents instead of passing through a lossy JavaScript Number. Property remains the source of calculated published totals.
- Standalone fixture fallback requires both existing test flags and does not fetch fake search data. `<h1>Buyer search</h1>`, the actor account ID and sign-out remain visible to active accounts. The original `sign-in.spec.ts` and `identity-stack.spec.ts` are unchanged.
- Three standalone checks cover URL round-trips, hostile/ambiguous context and precise prices; a focused `search-ui-stack.spec.ts` checks the existing Phase 1 plot through real filter controls and Back to Search. The independent multi-fixture search workflow remains in 5.4.

## Evidence

Verified **2026-11-28 (Asia/Colombo)** at implementation revision **`732a110a6ba8fad313a34b691f016c258c91982e`**. Phase 5.2 implementation/evidence `e114ae7` / `5b60491` were pushed and [CI passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46142226695) before this subphase began.

Exact full-suite command in the persistent Ubuntu WSL Linux copy:

```sh
export PATH=/home/sandaru/.nvm/versions/node/v24.22.3/bin:/usr/local/bin:/usr/bin:/bin
source /home/sandaru/.venvs/estateflow/bin/activate
python project/tests/integration/identity_acceptance.py
```

The runner exited **0**: frontend lint/build/typecheck passed; **14 standalone checks** (the unchanged **11 OIDC tests** plus **3 navigation/format checks**) passed in 20.6 s; Alembic reached **0001 (head)** with original SQL assertions intact; **37 Property tests** passed in 15.158 s under PostgreSQL 17's scoped **estateflow_property** login; **9 Engagement tests** passed in 1.907 s; and **6 Compose tests** passed in 40.1 s. Both service suites use `python -W error::ResourceWarning -m unittest discover -s project/services/{property,engagement}/tests -v`, once per service. Runtime grant-denial checks remain passing.

Frontend commands are `npm run lint`, `build`, `typecheck`, and standalone `test:e2e` with `project/frontend` as cwd. After adding the focused UI smoke test, `npm --prefix project/frontend run lint` and `npm --prefix project/frontend run typecheck` also passed on the final test source. The smoke test selected land, entered budget and cross-unit area criteria, verified the approximate LKR 5,000,000 published total and confirmed-access badge, opened the real listing, restored the exact prior URL/control values/result through Back to Search, and cleared the filters. Desktop and 390×844 screenshots were inspected; mobile document-width overflow assertion passed.

The pushed implementation/evidence head must pass CI before 5.4 begins. Final verified CI links are collected in the Phase 5.4 closeout record.
