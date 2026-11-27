# Phase 3.4 · CI and end-to-end draft acceptance

Integrate the Phase 3 Property and Frontend draft flows in Docker Compose, verify end-to-end acceptance across two authenticated accounts, and add deterministic Phase 3 checks to GitHub Actions CI.

[Phase 3](phase3.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 2.4 reference](../phase-02/phase2.4.md)

## Progress

- [x] Wire `ESTATEFLOW_PROPERTY_DATABASE_URL` and `ESTATEFLOW_PRIVATE_DETAIL_KEYS` / `ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF` into `project/compose.yaml`, `project/compose.identity-test.yaml`, and `.env.identity.example` (using non-production test values only).
- [x] Add end-to-end Playwright + API acceptance tests (under `project/frontend/tests/` and/or `project/tests/integration/`) running against the full local Compose stack (Frontend + Engagement + Property + PostgreSQL 17 + test identity provider):
  - Seller signs in, creates a draft, saves `0` and `unknown` fields, retries a save, manages encrypted private details (add, edit in place, remove, re-add), and reopens the draft.
  - Second authenticated account (buyer/other seller) attempts to read or edit the first seller's draft and private details and is denied.
- [x] Update `.github/workflows/` CI to run the Phase 3 Property unit/integration tests, frontend `lint`/`typecheck`/`build`, and Playwright draft E2E checks on pull requests.
- [x] Run the full local acceptance suite and record exact commands, Git revision, date, and observed results in the **Evidence** section below before ticking Phase 3 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts the test database and Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Frontend static checks, and Playwright draft E2E tests pass.
3. GitHub Actions CI passes on the Phase 3 pull request.

## Evidence

Verification date: 2026-11-28 (Asia/Colombo). Implementation revision: `d855b1910b8cf514ec4e94455f583d512665aec6` on [draft PR #7](https://github.com/BigBug-Mora/BigBug-university/pull/7).

From the repository root, the frontend and service checks use these commands:

```sh
npm --prefix project/frontend ci
npm --prefix project/frontend run lint
npm --prefix project/frontend run typecheck
npm --prefix project/frontend run build
npm --prefix project/frontend run test:e2e
python project/tests/integration/identity_acceptance.py
```

The Python runner applies Alembic, provisions both runtime logins, loads fictional fixtures, checks the schema head, and runs the following commands with disposable database URLs. It then builds the Compose images and runs Playwright with `ESTATEFLOW_TEST_IDENTITY_STACK=1`.

```sh
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v
python -W error::ResourceWarning -m unittest discover -s project/services/engagement/tests -v
```

Local setup used Ubuntu WSL Docker Engine and Compose. Windows ran the repository virtual environment (`.\.venv\Scripts\python.exe project/tests/integration/identity_acceptance.py`) with a temporary CLI bridge to WSL. Compose read a clean Linux archive of the implementation revision. A Windows-native Turbopack build failed while starting its PostCSS worker; the Linux runs exercised the deployment build.

| Check | Observed result |
| --- | --- |
| Frontend | Lint, TypeScript and the production build passed locally in Linux. All 11 standalone Playwright sign-in tests passed (53.4 s). Playwright used Chromium 1255; the local Windows driver installed it with `npm.cmd --prefix project/frontend exec -- playwright install chromium --only-shell`. |
| Database and services | Alembic reached `0001 (head)` on disposable PostgreSQL 17. The fixture and schema assertions, 12 Property tests and 9 Engagement tests passed. The probes used the scoped runtime logins. |
| Local full stack | All five services started. Both Playwright tests passed (45.8 s) with the WSL distribution kept active for the Windows runner. The runner removed the containers and network. The seller browser reopened house, apartment and land drafts, preserved zero/false/unknown, managed phone/address/pin slots and displayed a stale-save conflict. Authenticated API calls verified replay and second-account denials. |
| Pull-request CI | GitHub Actions passed at the implementation revision: frontend static checks, 11 standalone browser tests, 12 Property tests, 9 Engagement tests, and 2 Compose browser tests. [Verified job](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46053921359/job/140691691909) |
