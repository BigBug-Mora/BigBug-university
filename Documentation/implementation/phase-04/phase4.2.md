# Phase 4.2 · Published listing read API for signed-in buyers

Expose the buyer-facing published listing endpoint on `property-service` behind verified actor authentication, reading strictly from `property.current_publications` and isolating unpublished drafts and post-publication edits.

[Phase 4](phase4.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Database contracts](../../mvp/database/contracts.md#which-value-a-buyer-sees)

## Progress

- [ ] Add `GET /published-listings/{listing_id}` in `project/services/property/routes.py` and `publication.py` behind `require_frontend_actor` (permitting any active authenticated buyer or seller account).
- [ ] Apply `Cache-Control: no-store` middleware coverage to `/published-listings` routes alongside `/listings` in `project/services/property/app.py`.
- [ ] Query `property.current_publications` joined with `property.public_listings`, published `property.listing_revisions` (dedicated columns and `standard_fact_evidence`), `property.revision_facts` (`approved_for_public = true`) joined with `property.fact_versions` and `property.fact_definitions`, and `property.showcase_photos` / `property.showcase_featured_photos` (returning empty lists when no photos are attached).
- [ ] Never read `current_draft_revision_id`, `current_showcase_id`, unapproved `revision_facts`, or `property.private_details` in the published buyer read; return `404` (`"Listing unavailable"`) if the listing does not exist or has no `current_publications` row.
- [ ] Add PostgreSQL integration tests in `project/services/property/tests/test_publication.py` covering publication lifecycle, draft-vs-published price isolation, `per_unit` land total calculation + approximate flag, `approved_for_public` fact visibility, unauthorized `401`, and unpublished `404`.

## Acceptance check

Run `python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v` against disposable PostgreSQL 17 with `estateflow_property`.

| Scenario | Expected result |
| --- | --- |
| Unauthenticated `GET /published-listings/{id}` | Returns `401` with `Cache-Control: no-store`. |
| Draft-only listing | Returns `404` (`{"detail": "Listing unavailable"}`) to any buyer. |
| Published listing after a private draft price edit | Returns the original published price, revision number, and showcase; never leaks the unpublished draft price or private details. |
| Re-published listing with updated `(revision, showcase)` | Returns the new price and updated showcase fields immediately. |
| Land listing with `per_unit` pricing and approximate area | Returns `entered_price`, `price_area_unit`, calculated `total_asking_price`, and `total_derived_from_approximate_area = true`. |
