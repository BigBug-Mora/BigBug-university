# Phase 5.3 · Buyer Search UI and Back-to-Search restoration

Build the signed-in `/buyer/search` screen in `project/frontend/` and wire **Back to Search** navigation on `/buyer/listings/[listingId]` so returning from a listing restores the buyer's previous query and results.

[Phase 5](phase5.md) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md)

## Progress

- [ ] Extend `project/frontend/src/server/property.ts` with `searchPublishedListings(params)` calling `GET /published-listings?...` using the signed-in user's access token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN` (never exposing tokens to client components).
- [ ] Update `project/frontend/src/server/destinations.ts`:
  - Allow `returnDestination` to preserve valid query parameters on `/buyer/search?...` (and validated `/buyer/listings/{uuid}?search=...` return context) across Cognito sign-in redirects without permitting open redirects or invalid paths.
- [ ] Build the `/buyer/search` page (`project/frontend/src/app/buyer/search/page.tsx` and modular client filter/result components):
  - Keep `<h1>Buyer search</h1>` and show `actor.accountId` (plus graceful standalone fixture fallback when `ESTATEFLOW_TEST_STANDALONE_FIXTURES=1` and `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER=1`), preserving Phase 2 `sign-in.spec.ts` and `identity-stack.spec.ts` assertions.
  - Follow [UI design](../../mvp/containers/frontend/ui.md): tighter search spacing, consistent card proportions, predictable placement of headline, location (`Town, District`), formatted price (`entered_price` + calculated total & `"Approximate total"` badge for `per_unit` land), key facts (`Land area`, `Floor area`, `Bedrooms`, `Bathrooms`), and explicit vehicle-access badges (`Confirmed`, `No vehicle access`, `Unknown — needs confirmation`).
  - Provide structured filter controls (`property_type`, `district`, `town`, `currency`, `min_price`, `max_price`, `min_bedrooms`, `min_bathrooms`, `min_land_area` + `land_area_unit`, `vehicle_access`: `Any` / `Required (include unknown)` / `Confirmed only` / `No vehicle access`, plus `Clear filters`) synced via URL query parameters (`GET` navigation / `router.push`).
- [ ] Wire **Back to Search** on `project/frontend/src/app/buyer/listings/[listingId]/page.tsx`:
  - Search result cards link to `/buyer/listings/${id}?search=${encodeURIComponent(currentQuery)}` (only when `currentQuery` is non-empty).
  - `/buyer/listings/[listingId]` validates the `search` query param safely (stripping any non-search/unsafe characters, reconstructing `/buyer/search?...`) and renders `<Link href={backToSearchHref}>Back to Search</Link>` so clicking **Back to Search** restores the exact prior filters and results.
- [ ] Verify `npm --prefix project/frontend run lint`, `typecheck`, `build`, and standalone `test:e2e` pass with zero warnings/errors.

## Acceptance check

Verify frontend static checks and interactive search + navigation behavior against the local stack.

| Scenario | Expected result |
| --- | --- |
| `lint`, `typecheck`, `build`, standalone `test:e2e` | All pass cleanly with zero warnings or errors; `sign-in.spec.ts` passes unchanged. |
| Filter controls & result cards | Cards consistently show price (with calculated land total when `per_unit`), location, key measurements, and vehicle-access status badges. |
| Unknown vehicle access under `required` | Appears with an explicit `"Needs confirmation"` / `"Unknown"` badge after confirmed matches. |
| **Back to Search** navigation | Navigating from filtered search to a listing and clicking **Back to Search** restores the query URL, form values, and matching result set. |
