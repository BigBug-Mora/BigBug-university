# Phase 3.4 · CI and end-to-end draft acceptance

Integrate the Phase 3 Property and Frontend draft flows in Docker Compose, verify end-to-end acceptance across two authenticated accounts, and add deterministic Phase 3 checks to GitHub Actions CI.

[Phase 3](phase3.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 2.4 reference](../phase-02/phase2.4.md)

## Progress

- [ ] Wire `ESTATEFLOW_PROPERTY_DATABASE_URL` and `ESTATEFLOW_PRIVATE_DETAIL_KEYS` / `ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF` into `project/compose.yaml`, `project/compose.identity-test.yaml`, and `.env.identity.example` (using non-production test values only).
- [ ] Add end-to-end Playwright + API acceptance tests (under `project/frontend/tests/` and/or `project/tests/integration/`) running against the full local Compose stack (Frontend + Engagement + Property + PostgreSQL 17 + test identity provider):
  - Seller signs in, creates a draft, saves `0` and `unknown` fields, retries a save, manages encrypted private details (add, edit in place, remove, re-add), and reopens the draft.
  - Second authenticated account (buyer/other seller) attempts to read or edit the first seller's draft and private details and is denied.
- [ ] Update `.github/workflows/` CI to run the Phase 3 Property unit/integration tests, frontend `lint`/`typecheck`/`build`, and Playwright draft E2E checks on pull requests.
- [ ] Run the full local acceptance suite and record exact commands, Git revision, date, and observed results in the **Evidence** section below before ticking Phase 3 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts the test database and Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Frontend static checks, and Playwright draft E2E tests pass.
3. GitHub Actions CI passes on the Phase 3 pull request.

## Evidence

*Pending Phase 3 implementation and verification.*
