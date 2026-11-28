# Phase 4.4 · CI and end-to-end publication acceptance

Verify the complete Phase 4 seller-to-buyer publication flow across two authenticated accounts in Docker Compose and integrate the checks into GitHub Actions CI.

[Phase 4](phase4.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 3.4 reference](../phase-03/phase3.4.md)

## Progress

- [x] Add `project/frontend/tests/publication-stack.spec.ts` running against the full local Compose stack (`frontend` + `property-service` + `engagement-service` + PostgreSQL 17 + `identity-fixture`):
  - Seller signs in, creates a house draft with required fields and an active phone number, authors/applies a showcase fixture, previews it, and publishes the matching `(revision, showcase)` pair.
  - Signed-in buyer opens `/buyer/listings/{listingId}` and sees the published headline and original price (with the no-photo architectural header and no broken images).
  - Unauthenticated direct access to `/buyer/listings/{listingId}` redirects to `/sign-in?returnTo=...` and resumes the published listing after sign-in.
  - Seller saves a private draft price edit without re-publishing; buyer reloads `/buyer/listings/{listingId}` and still sees the **original** published price.
  - Seller cannot publish the new revision with the stale showcase (`409` feedback); after saving an updated showcase for the new revision and publishing the updated pair, buyer reloads and sees the **updated** price.
  - Draft-only (unpublished) listing returns unavailable (`404`) when requested by the buyer.
- [x] Verify `project/tests/integration/identity_acceptance.py` and `.github/workflows/ci.yml` execute all Phase 4 Property tests, Frontend static checks, standalone Playwright checks, and full-stack Playwright checks cleanly.
- [x] Record exact commands, Git revision, date, and observed results in **Evidence** below before ticking Phase 4 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts disposable PostgreSQL 17 and the Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Engagement tests, Frontend static checks, standalone sign-in tests, and Compose browser tests pass.
3. GitHub Actions CI passes on the Phase 4 pull request/commit.

## Evidence

Local verification date: **2026-11-28 (Asia/Colombo)**. Implementation revision: **`962e630f53b0cfc045ba29af4fa71ddd7ef5464a`**. Phase 4.3 was committed and pushed first as `8ef34ba`, with [successful CI](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46138700823).

The complete local gate ran from `/home/sandaru/estateflow-phase04` using Ubuntu WSL Docker Engine + Compose, the existing Python virtual environment, Node 24, and Playwright Chromium 1255:

```sh
python project/tests/integration/identity_acceptance.py
```

That runner executes these commands, in this order, with standalone fixture mode isolated from the real stack. Frontend commands run with `project/frontend` as the working directory (equivalent to `npm --prefix project/frontend run ...` from the root):

```sh
# cwd: project/frontend; ESTATEFLOW_TEST_IDENTITY_STACK=0
npm run lint
npm run build
npm run typecheck
npm run test:e2e
# cwd: repository root
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v
python -W error::ResourceWarning -m unittest discover -s project/services/engagement/tests -v
# cwd: project/frontend, after Compose starts all five services; ESTATEFLOW_TEST_IDENTITY_STACK=1
npm run test:e2e
```

The runner additionally provisions both scoped runtime logins, applies `infra/aws/grant-property-runtime.sql` as the migrator, loads fictional fixtures, and runs schema assertions before the service suites. It exited **0** and removed its disposable containers/network.

| Check | Final local observed result |
| --- | --- |
| Frontend lint, production build, TypeScript | All passed. |
| Standalone OIDC browser tests | **11/11 passed**, 23.7 s; original `sign-in.spec.ts` unchanged. |
| PostgreSQL / Property | Alembic **0001 (head)**, PostgreSQL **17**, runtime login **estateflow_property**, **26 tests passed**, 10.199 s. DDL, cross-schema, immutable-publication/showcase and seller-identity privilege-denial probes passed. |
| Engagement | **9 tests passed**, 2.126 s. |
| Full-stack browsers | **5/5 passed**, 40.3 s: drafts, identity/recovery, two-account publication lifecycle, unpublished/malformed listing access, and showcase UI/desktop/mobile presentation. |

The publication lifecycle used a seller browser to publish **LKR 15,000,000**, a separate unauthenticated buyer browser to sign in and resume that exact UUID listing, a private seller edit to **LKR 18,000,000**, buyer refresh/API checks retaining the original snapshot, explicit stale-pair **409** (API and UI), updated showcase preview/publication, and buyer refresh showing the new price and headline. The second publication test verified **401**, unpublished **404**, malformed-ID **422**, no-store headers, and rejection of the standalone slug by the real frontend stack. Published pages contained no image elements or private phone values.

GitHub Actions verification: **passed** on **2026-11-28 (Asia/Colombo)** at evidence revision **`17515e9069ce55d66e74b431045d628c9a0e9d4e`**, which contains implementation revision `962e630f53b0cfc045ba29af4fa71ddd7ef5464a`. [Successful Phase 4.4 run](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46139424367). The GitHub API confirmed `status=completed`, `conclusion=success` and the exact head SHA before completion checkboxes were ticked. The same complete acceptance runner executed in CI on Ubuntu 24.04 with Python 3.14 and Node 24. All Phase 4 acceptance requirements are complete; the phase plan and roadmap were checked only after this local-plus-CI gate.

## Sequential commit and CI record

The initial planning files were committed and pushed as `494b1bf` before subphase implementation. Each subphase's implementation and evidence commits were pushed before starting the next subphase.

| Subphase | Implementation commit | Evidence commit | Local Property / Engagement / standalone / stack counts | Verified CI |
| --- | --- | --- | --- | --- |
| 4.1 | `e56503d` | `4dec0e5` | 21 / 9 / 11 / 2 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46136668113) |
| 4.2 | `27041a4` | `7dd4088` | 26 / 9 / 11 / 2 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46137090420) |
| 4.3 | `10aeb9e` | `8ef34ba` | 26 / 9 / 11 / 3 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46138700823) |
| 4.4 | `962e630` | `17515e9` | 26 / 9 / 11 / 5 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46139424367) |

Frontend lint, production build and typecheck passed in every subphase. This final documentation/roadmap completion update is committed and pushed separately after verification.

## Implementation decisions

- `publication-stack.spec.ts` uses separate seller and buyer browser contexts. Seller creation, fact edits, phone saving, showcase authoring, preview and both publications run through the UI. Authenticated API probes verify the exact stale-pair `409`, original published snapshot, new revision/showcase IDs, unpublished `404`, unauthenticated `401`, and malformed-ID `422`.
- Fixture credentials and browser sign-in assertions live in `tests/stack-identity.ts`, shared with the existing draft acceptance test. The original standalone `sign-in.spec.ts` remains unchanged; the real stack also verifies that `courtyard-house` cannot resolve as a listing.
- `identity_acceptance.py` is now the complete local and CI gate: lint → production build → typecheck → standalone OIDC tests → disposable PostgreSQL 17 migrations/grants and both service suites → Compose browser tests. The standalone subprocess explicitly uses `ESTATEFLOW_TEST_IDENTITY_STACK=0`; full-stack tests retain `1`. CI installs dependencies/Chromium and calls this runner once.
- Browser subprocess timeouts are bounded at 180 seconds for standalone checks and 240 seconds for the expanded Compose suite. Fixture browser actions have short timeouts, so a missing control fails at the affected step.
- Acceptance review found that a normal draft-form round trip expands omitted evidence metadata to explicit nulls. Publication now treats omitted and null optional metadata identically when comparing dedicated-field evidence, preserving independent chat corrections on unrelated edits. The existing PostgreSQL reconciliation regression now exercises the actual editor payload shape. This is a correction to the Phase 4.1 contract discovered during final acceptance, not an additional workflow.
