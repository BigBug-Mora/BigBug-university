# Phase 4.3 · Seller preview, publication UI, and buyer listing page

Build the seller showcase editor, preview screen, and publish controls under `/seller/workspace/[listingId]`, and replace the placeholder buyer route at `/buyer/listings/[listingId]` with the Courtyard-House-styled published listing page.

[Phase 4](phase4.md) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md) · [Courtyard House showcase](../../mvp/showcase/index.html)

## Progress

- [x] Extend `project/frontend/src/server/property.ts` and `project/frontend/src/app/seller/workspace/actions.ts` with server-side helpers and actions for `GET /listings/{id}/showcase`, `POST /listings/{id}/showcases`, `POST /listings/{id}/publish`, and `GET /published-listings/{id}` (using the signed-in user's token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN`).
- [x] Build a shared showcase presentation component (`project/frontend/src/components/listing-showcase.tsx`) following [UI design](../../mvp/containers/frontend/ui.md) and [Courtyard House showcase](../../mvp/showcase/index.html):
  - Warm paper palette (`#F7F4EB` light / `#21231D` dark), `Instrument Serif` headings, `DM Sans` body and controls, hairline borders, tabular numbers, and accessible focus styles.
  - Render the resolved no-photo layout cleanly when `gallery_photos` is empty (typographic architectural header card with `"No photos published yet"`, omitting cover/story/gallery containers), while supporting cover photo, 3-item alternating featured story, and bottom gallery grids when photos are present (Phase 06+).
  - Display formatted asking price (including `per_unit` calculated total and approximate label), key metrics strip, highlights, description, and published property facts with explicit `"Yes"`/`"No"`/`"0"`/`"Unknown"` and approximate/seller-stated provenance.
- [x] Add seller showcase & publication controls in `project/frontend/src/app/seller/workspace/[listingId]/` (including an authored showcase fixture loader, editable headline/description/highlights, explicit `access_road_width` public-visibility toggle in the draft editor, live publication readiness/status summary, `/seller/workspace/[listingId]/preview` route, and idempotent **Publish listing** button).
- [x] Replace `project/frontend/src/app/buyer/listings/[listingId]/page.tsx` with the signed-in buyer published listing page (enforcing `protectedAccount(...)`, calling `GET /published-listings/{listingId}` for UUID listings, rendering `"Listing unavailable"` on `404`, and preserving Phase 2's standalone `"courtyard-house"` fixture check).
- [x] Verify `npm --prefix project/frontend run lint`, `typecheck`, and `build` pass with zero warnings/errors.

## Acceptance check

Verify frontend static checks and interactive preview/publish/buyer views against the local stack.

| Scenario | Expected result |
| --- | --- |
| `lint`, `typecheck`, and `build` | All pass with zero warnings or errors. |
| Seller showcase fixture & preview | Seller applies/edits showcase copy for the current draft, previews it on `/seller/workspace/[listingId]/preview`, and sees a non-published preview banner. |
| Seller publish & validation feedback | Missing required fields or missing phone number blocks publish with clear feedback; complete draft + phone + matching showcase publishes cleanly and links to the buyer page. |
| Buyer published listing page (no photos) | Displays the typographic header card without broken image tags, shows published price, highlights, description, and grounded fact labels. |

## Implementation decisions

- Standalone OIDC compatibility requires both `ESTATEFLOW_TEST_STANDALONE_FIXTURES=1` and the existing HTTP test-issuer switch. Only the standalone Playwright web server receives that fixture flag. The Compose identity test now uses `/buyer/search` for its account/logout checks; stack and production listing routes validate UUIDs and fetch real publications.
- The existing identity outage test restores Engagement in `finally` and verifies authenticated seller-workspace recovery, so the new showcase UI check does not inherit a stopped or still-starting dependency. Compose's running-process state alone was insufficient after the deliberate outage.
- Buyer totals come from Property's public projection. An unpublished seller preview formats the same entered amount/unit and uses the immutable seeded area conversion factors only for its display total. It never writes a derived price. Unknown precision stays unspecified; approximate areas label the calculated total approximate.
- Authored starters use property type and coarse location only; they do not invent amenities or photos. Seller preview refuses to combine current facts with a stale showcase. Publish still sends the explicit pair to Property so stale-pair and required-field feedback comes from the owning service.
- Idempotent showcase/publish submissions reuse the existing session-storage action mechanism, with separate operation scopes. Saving facts refreshes readiness while preserving local feedback. Phone retirement now surfaces Property's last-active-phone validation message.
- `showcase-stack.spec.ts` verifies the Phase 4.3 UI path and captures desktop/mobile screenshots. The two-account private-edit isolation workflow remains in Phase 4.4.

## Evidence

Verified 2026-11-28 (Asia/Colombo), implementation revision `10aeb9e96366dc39242921e5839d8170d27f75ad`. Phase 4.2 had already been pushed as `7dd4088` with [successful CI](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46137090420).

Commands from the repository root in the persistent Ubuntu WSL Linux copy:

```sh
npm --prefix project/frontend run lint
npm --prefix project/frontend run build
npm --prefix project/frontend run typecheck
npm --prefix project/frontend run test:e2e
python project/tests/integration/identity_acceptance.py
```

Lint, production build and TypeScript passed with zero check failures. Standalone OIDC Playwright passed **11/11** (23.5 s), preserving the original `sign-in.spec.ts` and its `courtyard-house` slug. The final full-stack runner exited **0**: **26 Property tests** (10.788 s) with the scoped PostgreSQL 17 `estateflow_property` login, **9 Engagement tests** (2.260 s), and **3 Compose browser tests** (32.3 s). Both service suites run with `python -W error::ResourceWarning -m unittest discover -s project/services/{property,engagement}/tests -v`, once per service. Grant-denial checks passed unchanged.

The new UI test authors an incomplete showcase, confirms publication validation, saves a complete house with zero/false/unknown values and an explicitly public road width, adds a private phone, saves matching copy, previews, publishes, and opens the buyer page through browser controls. It asserts the no-photo note, zero image elements, published price, public width, and absence of the private phone. Desktop (1280 px) and mobile (390 px) screenshots were inspected; mobile overflow assertion passed. Visual review led to trimming database-scale trailing zeros in displayed measurements while preserving values and precision flags.

Earlier test attempts exposed two test-harness issues: the deliberate outage needed authenticated recovery after restarting Engagement, and exact dropdown-label selectors included option text. The final test uses accessible combobox names and explicit recovery checks. The final normal application flow passes without skips or weakened assertions.

