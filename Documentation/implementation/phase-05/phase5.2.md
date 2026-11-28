# Phase 5.2 · Search fixtures and PostgreSQL integration tests

Add comprehensive search fixtures and PostgreSQL 17 integration tests in `project/services/property/tests/test_search.py` covering all three property types, tri-state vehicle access, per-unit land price calculation, area-unit conversion, and draft/private-detail isolation.

[Phase 5](phase5.md) · [Phase 5.1](phase5.1.md) · [Public search schema](../../mvp/database/schema.md#6-publication-and-public-search)

## Progress

- [x] Keep `project/tests/fixtures/listings.sql` and `project/tests/integration/assert_database.sql` consistent (do not break Phase 1's single-published-plot SQL assertion), and build a reusable search fixture helper in `project/services/property/tests/test_search.py` using the real draft → showcase → publish API path.
- [x] Add `project/services/property/tests/test_search.py` covering:
  - Published listings across `house`, `apartment`, and `land` with distinct `vehicle_access` values (`true` confirmed, `false` explicitly no access, `None` unknown), plus an unpublished draft and active private details (`phone`, `written_address`, `map_pin`).
  - `GET /published-listings` filtering by `property_type`, `district`, `town` (including SQL LIKE wildcard escaping for `%` / `_`), `min_bedrooms` (preserving `0` vs `NULL`), `min_bathrooms`, `min_land_area` + `land_area_unit` (cross-unit conversion e.g. `perch` query matching `acre` listing), `min_floor_area` + `floor_area_unit` (`sq_m` vs `sq_ft`).
  - `vehicle_access` filter modes (`any`, `required`, `confirmed`, `none`), verifying ordering and `match_status` / `vehicle_access_status`.
  - `per_unit` land price evaluation against `min_price`/`max_price` (e.g. `250000` per `perch` on `0.125 acre` = `5000000.00` total passes `max_price=5500000` and is excluded by `max_price=4500000` and `min_price=5500000`), and currency scoping.
  - Draft isolation: a post-publish private price edit or unpublished draft never leaks into `GET /published-listings` results until re-published.
  - Security & runtime role checks: `401` when unauthenticated, `Cache-Control: no-store`, zero private detail leakage in JSON payloads, and execution under `estateflow_property`.
- [x] Run the full Property and Engagement suites locally against disposable PostgreSQL 17 and verify zero warnings/failures.

## Acceptance check

Run `python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Search across `true`, `false`, and `NULL` vehicle access | `required` distinguishes confirmed vs unknown (`needs_confirmation`) and omits `false`; `confirmed` omits `NULL`; `none` returns `false` only. |
| Land `per_unit` budget filter | Evaluates `total_asking_price` accurately across `perch`/`acre`/`hectare`/`sq_m`/`sq_ft`. |
| Cross-unit area filter | `min_land_area=15&land_area_unit=perch` matches `0.125 acre` (`20 perches`). |
| Post-publish private edit & unpublished draft | Search returns only the published snapshot and never returns unpublished drafts or private details. |

## Contract decisions

- Each test owns a unique district/town namespace and creates its own fixtures through draft creation, encrypted-phone saving, authored showcase saving, and explicit publication. Tests do not edit seed SQL, mutate publication timestamps, or need migrator privileges. The original one-publication SQL assertion still runs before these API-created fixtures.
- Search filters use exact Decimal unit factors from PostgreSQL. Tests cover boundary equality and values just above the boundary across all five land units, both floor-area units, and per-unit price denominators in all five units. Numeric minima exclude unknowns while retaining explicit zero counts at a zero minimum.
- The shared API fixture helper is confined to `test_search.py`; production search code and grants are unchanged in this subphase. Independent private-detail, unpublished-draft, private-price-edit and republish checks verify the public projection through normal HTTP operations.

## Evidence

Verified **2026-11-28 (Asia/Colombo)** at implementation revision **`e114ae74efc0f666497acdc513892103630c090d`**. Phase 5.1 implementation/evidence had already been pushed as `4f26793` / `0dbd828`, and [CI passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46141489016) before this subphase began.

Exact command, from the persistent Ubuntu WSL Linux copy with Node 24 and the existing Python environment:

```sh
export PATH=/home/sandaru/.nvm/versions/node/v24.22.3/bin:/usr/local/bin:/usr/bin:/bin
source /home/sandaru/.venvs/estateflow/bin/activate
python project/tests/integration/identity_acceptance.py
```

The complete runner exited **0**: frontend lint/build/typecheck passed, **11 standalone OIDC tests** passed (23.1 s), Alembic reached **0001 (head)** with the original SQL assertions intact, **37 Property tests** passed (18.637 s), **9 Engagement tests** passed (2.445 s), and **5 Compose browser tests** passed (42.2 s). Both service suites ran with `python -W error::ResourceWarning -m unittest discover -s project/services/{property,engagement}/tests -v`, once per service, under their scoped runtime logins on disposable PostgreSQL **17**. The search tests explicitly assert `estateflow_property` and denial of area-unit mutation. No migrations, grant changes or production-code changes were needed.

Nine new integration tests cover all property types, all vehicle modes and required-mode ordering, escaped text/case matching, five per-unit pricing denominators and five land-area query units, both floor-area units, inclusive price bounds/currency isolation, zero/unknown counts, deterministic paginated results and empty-page totals, unpublished/private-draft isolation and republishing, private phone/address/pin exclusion, authentication, invalid query combinations and no-store headers. The original Phase 1–4 tests remain passing.

GitHub Actions [passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46142226695) at evidence head `5b6049130bfe9e71c0e953093e53be0ff3a7c7d7`, verified before 5.3 began. The final Phase 5.4 closeout collects all subphase commits and CI links.
