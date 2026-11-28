# Phase 5.1 · Property structured search endpoint

Implement the structured search endpoint `GET /published-listings` in `project/services/property/` behind `require_frontend_actor`, querying `property.public_listings` with tri-state vehicle access, calculated total land pricing, and area-unit normalization.

[Phase 5](phase5.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Public search schema](../../mvp/database/schema.md#6-publication-and-public-search) · [Buyer search](../../mvp/containers/agent-api/buyer-agent.md#search-mode)

## Progress

- [ ] Confirm `estateflow_property` runtime grants in `infra/aws/grant-property-runtime.sql` already cover `SELECT` on `property.public_listings` and `property.area_units` (and `property.showcase_photos` / `property.listing_revisions` if needed); extend grants only if a missing read privilege is surfaced on disposable PostgreSQL 17.
- [ ] Add Pydantic query/filter validation in `project/services/property/models.py` (or a dedicated search schema) for:
  - `property_type` (`house` | `apartment` | `land`, optional)
  - `district` and `town` (optional non-empty text, case-insensitive substring `ILIKE` match with escaped wildcards)
  - `currency` (`^[A-Z]{3}$`, optional), `min_price` / `max_price` (`Decimal > 0`; validate `min_price <= max_price` when both are set, and require `currency` when a price bound is supplied or default cleanly per contract)
  - `min_bedrooms` (`int >= 0`), `min_bathrooms` (`int >= 0`)
  - `min_land_area` + `land_area_unit` (`AreaUnit`), `min_floor_area` + `floor_area_unit` (`sq_ft` | `sq_m`) — require unit whenever minimum area is supplied, normalizing against `property.area_units.square_metres`
  - `vehicle_access`: `any` (default) | `required` | `confirmed` | `none`
  - `limit` (1–50, default 20) and `offset` (`>= 0`, default 0)
- [ ] Implement structured search query builder in `project/services/property/published.py` (or `search.py`), exposed as `GET /published-listings` in `project/services/property/routes.py` with `Cache-Control: no-store`:
  - Read strictly from `property.public_listings` (never drafts, never `private_details`).
  - Evaluate `min_price` / `max_price` against `total_asking_price` (already calculated in `property.public_listings` for `per_unit` land listings) and return `entered_price`, `price_basis`, `price_area_unit`, `total_asking_price`, and `total_derived_from_approximate_area`.
  - Handle `vehicle_access`:
    - `any`: include `true`, `false`, and `NULL`
    - `required`: include `true` (`match_status = 'matched'`) and `NULL` (`match_status = 'needs_confirmation'`), excluding `false`; sort confirmed matches before `needs_confirmation`
    - `confirmed`: include `true` only (`match_status = 'matched'`)
    - `none`: include `false` only (`match_status = 'matched'`)
  - Return `{ "items": [...], "total": int, "limit": int, "offset": int }` with `vehicle_access_status` (`"confirmed"` | `"false"` | `"unknown"`), `match_status`, `cover_photo: null` (populated in Phase 06), and `published_at DESC, listing_id ASC` deterministic ordering.
- [ ] Verify invalid query combinations (e.g. `min_price > max_price`, `min_land_area` without `land_area_unit`, malformed `currency`) return `422`.

## Acceptance check

Exercise `GET /published-listings` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Unauthenticated `GET /published-listings` | Returns `401` with `Cache-Control: no-store`. |
| `vehicle_access=required` across `true`, `false`, `NULL` listings | Returns `true` (`matched`) first, `NULL` (`needs_confirmation`) second, and excludes `false`. |
| `vehicle_access=confirmed` and `vehicle_access=none` | Returns only `true` or only `false` respectively. |
| `per_unit` land listing with `min_price`/`max_price` | Evaluated by `total_asking_price` (not raw `entered_price`), preserving `total_derived_from_approximate_area`. |
| Invalid filter (e.g. `min_price > max_price` or area without unit) | Returns `422`. |
