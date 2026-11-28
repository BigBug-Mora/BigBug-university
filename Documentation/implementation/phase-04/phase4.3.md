# Phase 4.3 · Seller preview, publication UI, and buyer listing page

Build the seller showcase editor, preview screen, and publish controls under `/seller/workspace/[listingId]`, and replace the placeholder buyer route at `/buyer/listings/[listingId]` with the Courtyard-House-styled published listing page.

[Phase 4](phase4.md) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md) · [Courtyard House showcase](../../mvp/showcase/index.html)

## Progress

- [ ] Extend `project/frontend/src/server/property.ts` and `project/frontend/src/app/seller/workspace/actions.ts` with server-side helpers and actions for `GET /listings/{id}/showcase`, `POST /listings/{id}/showcases`, `POST /listings/{id}/publish`, and `GET /published-listings/{id}` (using the signed-in user's token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN`).
- [ ] Build a shared showcase presentation component (`project/frontend/src/components/listing-showcase.tsx`) following [UI design](../../mvp/containers/frontend/ui.md) and [Courtyard House showcase](../../mvp/showcase/index.html):
  - Warm paper palette (`#F7F4EB` light / `#21231D` dark), `Instrument Serif` headings, `DM Sans` body and controls, hairline borders, tabular numbers, and accessible focus styles.
  - Render the resolved no-photo layout cleanly when `gallery_photos` is empty (typographic architectural header card with `"No photos published yet"`, omitting cover/story/gallery containers), while supporting cover photo, 3-item alternating featured story, and bottom gallery grids when photos are present (Phase 06+).
  - Display formatted asking price (including `per_unit` calculated total and approximate label), key metrics strip, highlights, description, and published property facts with explicit `"Yes"`/`"No"`/`"0"`/`"Unknown"` and approximate/seller-stated provenance.
- [ ] Add seller showcase & publication controls in `project/frontend/src/app/seller/workspace/[listingId]/` (including an authored showcase fixture loader, editable headline/description/highlights, explicit `access_road_width` public-visibility toggle in the draft editor, live publication readiness/status summary, `/seller/workspace/[listingId]/preview` route, and idempotent **Publish listing** button).
- [ ] Replace `project/frontend/src/app/buyer/listings/[listingId]/page.tsx` with the signed-in buyer published listing page (enforcing `protectedAccount(...)`, calling `GET /published-listings/{listingId}` for UUID listings, rendering `"Listing unavailable"` on `404`, and preserving Phase 2's standalone `"courtyard-house"` fixture check).
- [ ] Verify `npm --prefix project/frontend run lint`, `typecheck`, and `build` pass with zero warnings/errors.

## Acceptance check

Verify frontend static checks and interactive preview/publish/buyer views against the local stack.

| Scenario | Expected result |
| --- | --- |
| `lint`, `typecheck`, and `build` | All pass with zero warnings or errors. |
| Seller showcase fixture & preview | Seller applies/edits showcase copy for the current draft, previews it on `/seller/workspace/[listingId]/preview`, and sees a non-published preview banner. |
| Seller publish & validation feedback | Missing required fields or missing phone number blocks publish with clear feedback; complete draft + phone + matching showcase publishes cleanly and links to the buyer page. |
| Buyer published listing page (no photos) | Displays the typographic header card without broken image tags, shows published price, highlights, description, and grounded fact labels. |

