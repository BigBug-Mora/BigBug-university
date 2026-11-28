# Phase 4.2 · Published listing read API for signed-in buyers

Expose the buyer-facing published listing endpoint on `property-service` behind verified actor authentication, reading strictly from `property.current_publications` and isolating unpublished drafts and post-publication edits.

[Phase 4](phase4.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Database contracts](../../mvp/database/contracts.md#which-value-a-buyer-sees)

## Progress

- [x] Add `GET /published-listings/{listing_id}` in `project/services/property/routes.py` and `publication.py` behind `require_frontend_actor` (permitting any active authenticated buyer or seller account).
- [x] Apply `Cache-Control: no-store` middleware coverage to `/published-listings` routes alongside `/listings` in `project/services/property/app.py`.
- [x] Query `property.current_publications` joined with `property.public_listings`, published `property.listing_revisions` (dedicated columns and `standard_fact_evidence`), `property.revision_facts` (`approved_for_public = true`) joined with `property.fact_versions` and `property.fact_definitions`, and `property.showcase_photos` / `property.showcase_featured_photos` (returning empty lists when no photos are attached).
- [x] Never read `current_draft_revision_id`, `current_showcase_id`, unapproved `revision_facts`, or `property.private_details` in the published buyer read; return `404` (`"Listing unavailable"`) if the listing does not exist or has no `current_publications` row.
- [x] Add PostgreSQL integration tests in `project/services/property/tests/test_publication.py` covering publication lifecycle, draft-vs-published price isolation, `per_unit` land total calculation + approximate flag, `approved_for_public` fact visibility, unauthorized `401`, and unpublished `404`.

## Acceptance check

Run `python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Unauthenticated `GET /published-listings/{id}` | Returns `401` with `Cache-Control: no-store`. |
| Draft-only listing | Returns `404` (`{"detail": "Listing unavailable"}`) to any buyer. |
| Published listing after a private draft price edit | Returns the original published price, revision number, and showcase; never leaks the unpublished draft price or private details. |
| Re-published listing with updated `(revision, showcase)` | Returns the new price and updated showcase fields immediately. |
| Land listing with `per_unit` pricing and approximate area | Returns `entered_price`, `price_area_unit`, calculated `total_asking_price`, and `total_derived_from_approximate_area = true`. |

## Implementation decisions

- Keep buyer SQL in `project/services/property/published.py`, called by the publication API. The public view supplies price conversion and the publication identity; an explicit allowlist supplies additional dedicated public columns. Seller account IDs, revision action IDs, parent pointers, and fact source-account IDs are omitted.
- Anchor each follow-up read to the revision/showcase IDs selected by the initial published projection. Those records are immutable, so a concurrent publication cannot mix a new draft or showcase into this response. Chat-only overrides never feed the page.
- Media reads return ordered metadata from the exact showcase; Phase 06 will add authorized photo delivery. All Phase 04 authored showcases return empty media arrays.

## Evidence

Verified 2026-11-28 (Asia/Colombo), implementation revision `27041a416cd119f0e7b3caf1cd8b1b85cfb1d1cc`, after Phase 4.1 was pushed as `4dec0e5` ([successful CI](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46136668113)).

Exact commands, from the persistent Linux copy (`/home/sandaru/estateflow-phase04`) using Ubuntu WSL Docker Engine and Compose:

```sh
python project/tests/integration/identity_acceptance.py
npm --prefix project/frontend run lint
npm --prefix project/frontend run build
npm --prefix project/frontend run typecheck
npm --prefix project/frontend run test:e2e
```

The runner exited **0**: Alembic `0001 (head)`, **26 Property tests** (11.348 s) under the scoped `estateflow_property` PostgreSQL 17 login, **9 Engagement tests** (2.626 s), and **2 Compose browser tests** (19.9 s). It ran both service suites with `python -W error::ResourceWarning -m unittest discover -s project/services/{property,engagement}/tests -v` (one command for each service). The grant-denial probes remained passing. Frontend lint, production build and TypeScript passed; standalone Playwright passed **11/11** (22.6 s).

The five new integration tests verify missing/unpublished/malformed IDs, no-store headers on success and errors, price/showcase isolation across private edits and stale-pair rejection, republished values, frozen public approval independent of chat pointers, exact per-unit acre-to-perch conversion, approximate-area propagation, and incomplete-publication rollback. Buyer payload checks exclude private values and seller/action/draft-pointer metadata.
