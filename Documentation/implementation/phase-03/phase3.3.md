# Phase 3.3 · Seller draft editor in Frontend

Build the signed-in seller workspace and listing draft editor in `project/frontend/` wired to the Phase 3.1–3.2 Property service endpoints.

[Phase 3](phase3.md) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md) · [Phase 2 frontend](../../implementation/phase-02/phase2.2.md)

## Progress

- [x] Add server-side Property draft & private-detail client helpers in `project/frontend/src/server/` using the signed-in session's Cognito access token and `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN` (never exposing tokens or secrets to client components).
- [x] Build the seller workspace listing index and draft editor under `project/frontend/src/app/seller/workspace/` (and nested draft route if appropriate, e.g. `/seller/workspace/listings/[listingId]`):
  - Follow [UI design](../../mvp/containers/frontend/ui.md) (`Instrument Serif` headings, `DM Sans` controls/body, `#F7F4EB`/`#36492E` palette, accessible labels, visible focus, tighter seller-tool spacing).
  - Support creating a new draft (`house`, `apartment`, or `land`) and reopening any existing draft owned by the signed-in seller.
  - Render property-type-specific fields and clear `0` / `false` vs `unknown` (unset) controls so `0` is never coerced to `unknown` or vice versa.
  - Support land `total` vs `per_unit` asking price with `price_area_unit`, area units (`sq_m`, `sq_ft`, `perch`, `acre`, `hectare` for land; `sq_m`, `sq_ft` for floor area), `approximate` toggles, and `access_road_width`.
  - Render private detail slots (up to 3 phone numbers, written address, map pin lat/lng) with explicit UI copy explaining that editing a shared detail updates it for existing recipients and removing it retires that detail ID.
- [x] Generate stable client `create_action_id` / `edit_action_id` UUIDs per submission so double-clicks or retries on ambiguous network errors reuse the same action ID rather than creating duplicate listings/revisions.
- [x] Handle validation errors, `409` stale-revision conflicts, `403`/`404` ownership denials, and expired sessions explicitly in the UI.
- [x] Verify `npm --prefix project/frontend run lint`, `typecheck`, and `build` pass with zero warnings/errors.

## Acceptance check

Run the frontend static checks and verify the seller workspace flows against the local Property service.

| Scenario | Expected result |
| --- | --- |
| `lint`, `typecheck`, and `build` | All pass cleanly with zero warnings. |
| Create, save, and reopen a draft | Seller selects property type, saves partial fields including `0`/`false` and `unknown`, reloads the page, and sees exact saved state. |
| Private details editor | Seller adds, edits in place, and removes phone/address/pin; UI explains recipient update and ID retirement behavior. |
| Validation / conflict / session expiry | Surfaced cleanly with actionable recovery instead of silent failure or lost form state. |

Verified on 2026-11-28 at `d855b1910b8cf514ec4e94455f583d512665aec6`. Lint, typecheck and the Linux production build passed. The Compose browser test reopened all three property types, preserved explicit zero and false, managed private detail slots and retained unsaved town text after a stale revision conflict. [Commands and results](phase3.4.md#evidence)
