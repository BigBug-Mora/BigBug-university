# Phase 4.4 · CI and end-to-end publication acceptance

Verify the complete Phase 4 seller-to-buyer publication flow across two authenticated accounts in Docker Compose and integrate the checks into GitHub Actions CI.

[Phase 4](phase4.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 3.4 reference](../phase-03/phase3.4.md)

## Progress

- [ ] Add `project/frontend/tests/publication-stack.spec.ts` running against the full local Compose stack (`frontend` + `property-service` + `engagement-service` + PostgreSQL 17 + `identity-fixture`):
  - Seller signs in, creates a house draft with required fields and an active phone number, authors/applies a showcase fixture, previews it, and publishes the matching `(revision, showcase)` pair.
  - Signed-in buyer opens `/buyer/listings/{listingId}` and sees the published headline and original price (with the no-photo architectural header and no broken images).
  - Unauthenticated direct access to `/buyer/listings/{listingId}` redirects to `/sign-in?returnTo=...` and resumes the published listing after sign-in.
  - Seller saves a private draft price edit without re-publishing; buyer reloads `/buyer/listings/{listingId}` and still sees the **original** published price.
  - Seller cannot publish the new revision with the stale showcase (`409` feedback); after saving an updated showcase for the new revision and publishing the updated pair, buyer reloads and sees the **updated** price.
  - Draft-only (unpublished) listing returns unavailable (`404`) when requested by the buyer.
- [ ] Verify `project/tests/integration/identity_acceptance.py` and `.github/workflows/ci.yml` execute all Phase 4 Property tests, Frontend static checks, standalone Playwright checks, and full-stack Playwright checks cleanly.
- [ ] Record exact commands, Git revision, date, and observed results in **Evidence** below before ticking Phase 4 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts disposable PostgreSQL 17 and the Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Engagement tests, Frontend static checks, standalone sign-in tests, and Compose browser tests pass.
3. GitHub Actions CI passes on the Phase 4 pull request/commit.

## Evidence

*(To be recorded after final verification runs.)*
