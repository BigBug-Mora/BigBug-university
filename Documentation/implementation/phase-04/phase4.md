# Phase 4 · Showcase preview and publication

Build showcase authoring/preview, explicit seller publication, and the published listing page for signed-in buyers using an authored showcase fixture. Resolve how the published listing page renders when a listing has no photos, and verify that private draft edits remain isolated from buyers until the seller publishes the updated `(revision, showcase)` pair. [Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md) · [Phase 3 handoff](../phase-03/phase3.md#downstream-handoff)

## Progress and order

- [ ] [4.1 · Property showcase store, preview, and publication transaction](phase4.1.md). Extend `estateflow_property` database grants, add authored showcase saving and seller preview read endpoints, and implement the atomic, idempotent `Publish` transaction with minimum-field and active-phone enforcement.
- [ ] [4.2 · Published listing read API for signed-in buyers](phase4.2.md). Expose `GET /published-listings/{listing_id}` behind `require_frontend_actor`, reading strictly from `property.current_publications` and `approved_for_public` facts, and verify isolation with PostgreSQL integration tests.
- [ ] [4.3 · Seller preview, publication UI, and buyer listing page](phase4.3.md). Add the seller showcase fixture/editor, preview route, and publish controls in `/seller/workspace/[listingId]`, and build the Courtyard-House-styled buyer listing page at `/buyer/listings/[listingId]` with the resolved no-photo layout.
- [ ] [4.4 · CI and end-to-end publication acceptance](phase4.4.md). Add Playwright full-stack acceptance checks across seller and buyer accounts and confirm local and CI checks pass before ticking Phase 4 in the roadmap.

## Scope and ownership

| Owner | Deliverable |
| --- | --- |
| Property | Owns `property.showcase_revisions`, `property.publications`, `property.current_publications`, and `property.buyer_visible_facts` updates during `Publish`. Validates minimum publication fields, 1–3 active private phones, matching `(listing_revision_id, showcase_id)` pairs, and serves buyer-facing reads from `property.current_publications` only. |
| Frontend | Owns the seller showcase editor, preview route (`/seller/workspace/[listingId]/preview`), publish controls, and the signed-in buyer published listing page (`/buyer/listings/[listingId]`) styled per [UI design](../../mvp/containers/frontend/ui.md) and [Courtyard House showcase](../../mvp/showcase/index.html). |
| AWS grants / CI | Updates `infra/aws/grant-property-runtime.sql` for showcase/publication privileges on `estateflow_property` and extends the Playwright + Property acceptance suite run by `.github/workflows/ci.yml`. |

Use the existing PostgreSQL 17 schema (`0001_initial_schema.sql`), Phase 2 actor verification, and Phase 3 draft/private-detail store. S3 photo uploads (Phase 06), structured buyer search (Phase 05), AI Showcase Creator generation (Phase 09), Property Chat (Phase 12), and private disclosures (Phase 14) remain out of scope and use empty photo arrays and an authored showcase fixture in this phase.

[Property service spec](../../mvp/containers/property-service/property-service.md) · [Listing revisions and publication](../../mvp/database/contracts.md#listing-revisions-and-publication) · [Which value a buyer sees](../../mvp/database/contracts.md#which-value-a-buyer-sees) · [Frontend spec](../../mvp/containers/frontend/frontend.md) · [UI design](../../mvp/containers/frontend/ui.md)

## Phase acceptance

1. A signed-in seller saves a valid draft (including at least one active private phone number), authors or applies a showcase fixture for that revision, previews it, and explicitly publishes the matching `(listing_revision_id, showcase_id)` pair.
2. A signed-in buyer opens `/buyer/listings/{listingId}` and sees the published headline, highlights, description, approved facts, and original asking price rendered with the intentional no-photo header layout.
3. The seller saves a private draft price edit in `/seller/workspace/{listingId}` without re-publishing; the buyer reloads `/buyer/listings/{listingId}` and continues to see the original published price.
4. Attempting to publish the new draft revision with the older showcase is rejected (`409 Conflict`) until a matching showcase is saved for the new revision; once the updated pair is published, the buyer sees the updated price.
5. Unpublished listings return `404` to buyers, unauthenticated buyers are redirected to `/sign-in?returnTo=...` and resumed after sign-in, and all unit, integration, static, and Playwright Compose checks pass locally and in CI.

## Decisions and open questions

- **No-photo listing layout (resolved 2026-11-28):** When `gallery_photos` is empty (all Phase 04 listings prior to Phase 06, and any future listing published without photos per [MVP agent details](../../mvp/agent-details/agent-details.md#8-acceptance-examples)), omit the cover photo container, featured photo story section, and bottom gallery rather than rendering broken images or fake stock photos. Render an intentional typographic architectural header card in the Courtyard House palette (`#E2DFCF` / `#343B2F` surface, hairline border, `Instrument Serif` headline, property type + location eyebrow, formatted price summary, and a muted `"No photos published yet"` note) above the highlights, description, and public facts table.
- **Authored showcase authoring before Phase 09:** Use `property.showcase_revisions` with `source_job_id = NULL` so sellers can save an authored showcase (either edited directly or pre-filled from a property-type-aware authored fixture) against `current_draft_revision_id`, preview it, and publish it without depending on RabbitMQ/Celery or Claude.
- **Buyer route compatibility with Phase 2 standalone fixture:** Keep `/buyer/listings/[listingId]` strictly protected via `protectedAccount(...)`. UUID listing IDs fetch `GET /published-listings/{listingId}` from Property service; the non-UUID `"courtyard-house"` slug used by Phase 2's standalone OIDC sign-in spec continues to resolve cleanly in standalone fixture mode without weakening production/stack validation.
- **Public approval of versioned facts (`access_road_width`):** Allow `Draft` saves to carry `access_road_width_approved_for_public` (defaulting to `false` on new facts and preserved across parent revisions unless explicitly changed), recording `approved_by` and `approved_at` in `property.revision_facts` so `Publish` can reconcile `property.buyer_visible_facts` as specified in [contracts.md](../../mvp/database/contracts.md#which-value-a-buyer-sees).

## Downstream handoff

Phase 5 queries `property.public_listings` for structured buyer search and links search results to `/buyer/listings/[listingId]` with Back to Search state. Phase 6 populates `property.photos`, `property.revision_photos`, `property.showcase_photos`, and `property.showcase_featured_photos` so the shared showcase view renders real S3 photos alongside the no-photo fallback. Phase 9 populates `property.showcase_revisions` from `agent-worker` jobs with `source_job_id` set, using the same preview and publish pipeline.

