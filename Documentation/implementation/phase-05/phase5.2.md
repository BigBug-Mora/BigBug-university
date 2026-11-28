# Phase 5.2 · Search fixtures and PostgreSQL integration tests

Add comprehensive search fixtures and PostgreSQL 17 integration tests in `project/services/property/tests/test_search.py` covering all three property types, tri-state vehicle access, per-unit land price calculation, area-unit conversion, and draft/private-detail isolation.

[Phase 5](phase5.md) · [Phase 5.1](phase5.1.md) · [Public search schema](../../mvp/database/schema.md#6-publication-and-public-search)

## Progress

- [ ] Keep `project/tests/fixtures/listings.sql` and `project/tests/integration/assert_database.sql` consistent (do not break Phase 1's single-published-plot SQL assertion), and build a reusable search fixture helper in `project/services/property/tests/test_search.py` using the real draft → showcase → publish API path.
- [ ] Add `project/services/property/tests/test_search.py` covering:
  - Published listings across `house`, `apartment`, and `land` with distinct `vehicle_access` values (`true` confirmed, `false` explicitly no access, `None` unknown), plus an unpublished draft and active private details (`phone`, `written_address`, `map_pin`).
  - `GET /published-listings` filtering by `property_type`, `district`, `town` (including SQL LIKE wildcard escaping for `%` / `_`), `min_bedrooms` (preserving `0` vs `NULL`), `min_bathrooms`, `min_land_area` + `land_area_unit` (cross-unit conversion e.g. `perch` query matching `acre` listing), `min_floor_area` + `floor_area_unit` (`sq_m` vs `sq_ft`).
  - `vehicle_access` filter modes (`any`, `required`, `confirmed`, `none`), verifying ordering and `match_status` / `vehicle_access_status`.
  - `per_unit` land price evaluation against `min_price`/`max_price` (e.g. `250000` per `perch` on `0.125 acre` = `5000000.00` total passes `max_price=5500000` and is excluded by `max_price=4500000` and `min_price=5500000`), and currency scoping.
  - Draft isolation: a post-publish private price edit or unpublished draft never leaks into `GET /published-listings` results until re-published.
  - Security & runtime role checks: `401` when unauthenticated, `Cache-Control: no-store`, zero private detail leakage in JSON payloads, and execution under `estateflow_property`.
- [ ] Run the full Property and Engagement suites locally against disposable PostgreSQL 17 and verify zero warnings/failures.

## Acceptance check

Run `python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Search across `true`, `false`, and `NULL` vehicle access | `required` distinguishes confirmed vs unknown (`needs_confirmation`) and omits `false`; `confirmed` omits `NULL`; `none` returns `false` only. |
| Land `per_unit` budget filter | Evaluates `total_asking_price` accurately across `perch`/`acre`/`hectare`/`sq_m`/`sq_ft`. |
| Cross-unit area filter | `min_land_area=15&land_area_unit=perch` matches `0.125 acre` (`20 perches`). |
| Post-publish private edit & unpublished draft | Search returns only the published snapshot and never returns unpublished drafts or private details. |
