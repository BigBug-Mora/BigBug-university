# Phase 5.1 · Property structured search endpoint

Implement the structured search endpoint `GET /published-listings` in `project/services/property/` behind `require_frontend_actor`, querying `property.public_listings` with tri-state vehicle access, calculated total land pricing, and area-unit normalization.

[Phase 5](phase5.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Public search schema](../../mvp/database/schema.md#6-publication-and-public-search) · [Buyer search](../../mvp/containers/agent-api/buyer-agent.md#search-mode)

## Progress

- [x] Confirm `estateflow_property` runtime grants in `infra/aws/grant-property-runtime.sql` already cover `SELECT` on `property.public_listings` and `property.area_units` (and `property.showcase_photos` / `property.listing_revisions` if needed); extend grants only if a missing read privilege is surfaced on disposable PostgreSQL 17.
- [x] Add Pydantic query/filter validation in `project/services/property/models.py` (or a dedicated search schema) for:
  - `property_type` (`house` | `apartment` | `land`, optional)
  - `district` and `town` (optional non-empty text, case-insensitive substring `ILIKE` match with escaped wildcards)
  - `currency` (`^[A-Z]{3}$`, optional), `min_price` / `max_price` (`Decimal > 0`; validate `min_price <= max_price` when both are set, and require `currency` when a price bound is supplied or default cleanly per contract)
  - `min_bedrooms` (`int >= 0`), `min_bathrooms` (`int >= 0`)
  - `min_land_area` + `land_area_unit` (`AreaUnit`), `min_floor_area` + `floor_area_unit` (`sq_ft` | `sq_m`) — require unit whenever minimum area is supplied, normalizing against `property.area_units.square_metres`
  - `vehicle_access`: `any` (default) | `required` | `confirmed` | `none`
  - `limit` (1–50, default 20) and `offset` (`>= 0`, default 0)
- [x] Implement structured search query builder in `project/services/property/published.py` (or `search.py`), exposed as `GET /published-listings` in `project/services/property/routes.py` with `Cache-Control: no-store`:
  - Read strictly from `property.public_listings` (never drafts, never `private_details`).
  - Evaluate `min_price` / `max_price` against `total_asking_price` (already calculated in `property.public_listings` for `per_unit` land listings) and return `entered_price`, `price_basis`, `price_area_unit`, `total_asking_price`, and `total_derived_from_approximate_area`.
  - Handle `vehicle_access`:
    - `any`: include `true`, `false`, and `NULL`
    - `required`: include `true` (`match_status = 'matched'`) and `NULL` (`match_status = 'needs_confirmation'`), excluding `false`; sort confirmed matches before `needs_confirmation`
    - `confirmed`: include `true` only (`match_status = 'matched'`)
    - `none`: include `false` only (`match_status = 'matched'`)
  - Return `{ "items": [...], "total": int, "limit": int, "offset": int }` with `vehicle_access_status` (`"confirmed"` | `"false"` | `"unknown"`), `match_status`, `cover_photo: null` (populated in Phase 06), and `published_at DESC, listing_id ASC` deterministic ordering.
- [x] Verify invalid query combinations (e.g. `min_price > max_price`, `min_land_area` without `land_area_unit`, malformed `currency`) return `422`.

## Acceptance check

Exercise `GET /published-listings` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Unauthenticated `GET /published-listings` | Returns `401` with `Cache-Control: no-store`. |
| `vehicle_access=required` across `true`, `false`, `NULL` listings | Returns `true` (`matched`) first, `NULL` (`needs_confirmation`) second, and excludes `false`. |
| `vehicle_access=confirmed` and `vehicle_access=none` | Returns only `true` or only `false` respectively. |
| `per_unit` land listing with `min_price`/`max_price` | Evaluated by `total_asking_price` (not raw `entered_price`), preserving `total_derived_from_approximate_area`. |
| Invalid filter (e.g. `min_price > max_price` or area without unit) | Returns `422`. |

## Contract decisions

- Price bounds require an explicit uppercase currency; currency alone is also a valid filter. No currency conversion is performed. Area minima and their units must be supplied together in either direction, so incomplete filters are rejected rather than silently ignored.
- District/town filters trim surrounding whitespace, reject blank text and cap filter text at 160 characters. `%`, `_`, and the chosen SQL escape character `!` are escaped before binding an `ILIKE` substring parameter; backslashes remain literal.
- Search SQL is isolated in `project/services/property/search.py` and reads only the public view and area-unit reference data. The existing grants suffice; no migration or grant expansion is needed. A materialized CTE plus lateral page returns the total and items from one statement snapshot, including when offset is beyond the final result. Required-mode confirmed matches precede unknowns; publication time descending and listing UUID ascending break remaining ties.
- Counts of zero are valid minima. Missing numeric facts fail a numeric minimum; unknown vehicle access is explicitly retained only by `any`/`required`, as specified. The public view remains unchanged, preserving the original Phase 1 SQL fixture/assertion contract. Comprehensive independent publication fixtures remain scoped to 5.2.

## Evidence

Verified locally **2026-11-28 (Asia/Colombo)** at implementation revision **`4f267930e586adb3bc74af2e34d9475425636747`**. Plan setup was committed and pushed first as `f8db20aeafadf9e887cf07496ac9eededc9bbc82`.

Exact full-suite command in the persistent Ubuntu WSL Linux copy (`/home/sandaru/estateflow-phase04`, retained from Phase 04 with cached pinned dependencies):

```sh
export PATH=/home/sandaru/.nvm/versions/node/v24.22.3/bin:/usr/local/bin:/usr/bin:/bin
source /home/sandaru/.venvs/estateflow/bin/activate
python project/tests/integration/identity_acceptance.py
```

The runner exited **0**, including frontend lint/build/typecheck, **11 standalone OIDC tests** (24.4 s), Alembic **0001 (head)** and the original one-publication SQL fixture assertions, **28 Property tests** (11.965 s), **9 Engagement tests** (2.188 s), and **5 full-stack Compose tests** (42.0 s). Property tests used PostgreSQL **17** and **estateflow_property**, including the existing privilege-denial probes. No grant expansion was required. Both service suites ran with `python -W error::ResourceWarning -m unittest discover -s project/services/{property,engagement}/tests -v`, once per service; frontend commands are `npm run lint`, `build`, `typecheck`, and `test:e2e` with `project/frontend` as cwd, followed by stack `test:e2e` with `ESTATEFLOW_TEST_IDENTITY_STACK=1`.

The new query tests verify invalid related filters, non-finite values, authenticated public-view reads with calculated **LKR 5,000,000** land pricing, cross-unit minimum area, no-store headers, and an empty page beyond the final offset retaining its total. An additional TestClient probe against the same disposable runtime database exercised all vehicle modes after the publication tests: `any` returned 14 records, `required` returned 13 with confirmed matches before `needs_confirmation`, `confirmed` returned 1 true record, and `none` returned 1 false record. It asserted that all three states were present and false was excluded from required mode. Probe command: `PYTHONPATH=. /home/sandaru/.venvs/estateflow/bin/python /mnt/c/Users/ADMIN/Desktop/BigBug-university/.venv/phase05-search-probe.py` (temporary verification helper; independent committed fixtures follow in 5.2).

GitHub Actions must pass at the pushed implementation/evidence head before starting 5.2. Its verified run link is collected in the final Phase 5.4 closeout record.
