# Phase 5.4 · CI and end-to-end search acceptance

Verify the complete Phase 5 structured search and Back-to-Search workflow across authenticated seller and buyer sessions in Docker Compose and confirm GitHub Actions CI passes.

[Phase 5](phase5.md) · [CI design](../../mvp/ci/cd/ci.md) · [Phase 4.4 reference](../phase-04/phase4.4.md)

## Progress

- [x] Add `project/frontend/tests/search-stack.spec.ts` running against the full local Compose stack (`frontend` + `property-service` + `engagement-service` + PostgreSQL 17 + `identity-fixture`):
  - Seller API/UI publishes representative listings distinguishing:
    1. `land` with `per_unit` pricing (`250000 LKR / perch`, `0.125 acre` = `5,000,000 LKR` calculated total, `land_area_approximate = true`) and `vehicle_access = true` (confirmed).
    2. `house` with `vehicle_access = false` (explicitly no vehicle access), `bedroom_count = 0`, `parking_spaces = 0`.
    3. `apartment` (or `land`) with `vehicle_access = null` (unknown).
    4. An unpublished draft listing (must never appear in search).
  - Unauthenticated buyer navigating directly to `/buyer/search?property_type=land&vehicle_access=required` is redirected to `/sign-in` and resumes `/buyer/search?property_type=land&vehicle_access=required` after sign-in.
  - Signed-in buyer filters by vehicle access (`any`, `required`, `confirmed`, `none`), confirming `confirmed` vs `unknown` (`needs confirmation`) vs `false` behavior.
  - Buyer filters land by `max_price` (e.g., `5500000` includes the `250000/perch` plot and shows its approximate calculated total; `4500000` excludes it) and by cross-unit area (`min_land_area=15&land_area_unit=perch`).
  - Buyer opens a listing from the filtered results, verifies the published listing page, clicks **Back to Search**, and confirms the previous filters, URL query string, and matching result cards are restored.
  - Verify `Cache-Control: no-store`, zero private phone numbers in search responses/DOM, and desktop + mobile (`390×844`) responsive layout without horizontal overflow.
- [x] Run the full local acceptance suite (`python project/tests/integration/identity_acceptance.py`) and verify GitHub Actions CI passes.
- [x] Record exact commands, Git revision, date, and observed results in **Evidence** below before ticking Phase 5 in [roadmap.md](../roadmap.md).

## Acceptance check

1. Clean checkout starts disposable PostgreSQL 17 and the Compose stack with the deterministic identity provider.
2. All Property unit/integration tests, Engagement tests, Frontend static checks, standalone sign-in tests, and Compose browser tests (including `search-stack.spec.ts`) pass.
3. GitHub Actions CI passes on the Phase 5 commits.

## Evidence

Local verification date: **2026-11-28 (Asia/Colombo)**. Implementation revision: **`0b60d0664394d0e3a8790d693af858e1d7960507`**. Phase 5.3 implementation/evidence `732a110` / `0913b60` were pushed and [CI passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46143424358) before this subphase began.

Exact full local gate, run in the persistent Ubuntu WSL Docker Engine + Compose copy (`/home/sandaru/estateflow-phase04`) with Node 24.22.3 and the existing Python virtual environment:

```sh
export PATH=/home/sandaru/.nvm/versions/node/v24.22.3/bin:/usr/local/bin:/usr/bin:/bin
source /home/sandaru/.venvs/estateflow/bin/activate
python project/tests/integration/identity_acceptance.py
```

The runner executed these commands in order, provisioning disposable database/runtime roles and applying their existing grants before the service suites:

```sh
# cwd: project/frontend; ESTATEFLOW_TEST_IDENTITY_STACK=0
npm run lint
npm run build
npm run typecheck
npm run test:e2e
# cwd: repository root, after starting disposable PostgreSQL 17
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v
python -W error::ResourceWarning -m unittest discover -s project/services/engagement/tests -v
# cwd: project/frontend, after Compose builds and starts all five services; ESTATEFLOW_TEST_IDENTITY_STACK=1
npm run test:e2e
```

| Check | Final local observed result |
| --- | --- |
| Frontend lint, production build and typecheck | Passed. |
| Standalone checks | **14 passed**, 19.6 s: the unchanged **11 OIDC tests** plus **3 search navigation/price checks**. |
| Database / Property | Alembic **0001 (head)**; original one-publication SQL fixture assertions passed; PostgreSQL **17**, scoped **estateflow_property** login, **37 tests passed**, 15.612 s. Existing and new privilege-denial probes passed without additional grants. |
| Engagement | **9 tests passed**, 1.975 s. |
| Compose browser acceptance | **7 passed**, 45.1 s, including the full search workflow, focused search UI, identity/recovery, drafts, publication lifecycle/unavailable access, and showcase UI. |

The runner exited **0** and removed its disposable containers/network. After the final pagination assertion, `npm --prefix project/frontend run lint` and `npm --prefix project/frontend run typecheck` also passed on the final test source.

The new browser case verified all four vehicle modes; required-mode confirmed-first ordering and explicit unknown status; a per-perch plot included at a LKR 5,500,000 maximum and excluded at LKR 4,500,000 or a LKR 5,500,000 minimum; acre-to-perch land minima and square-metre-to-square-foot floor minima; zero bedrooms/parking distinct from unknowns; unpublished exclusion and `404`; unauthorized search `401`; no-store API/frontend responses; no private phone/address/pin or service credential values in results/DOM; search and nested listing context sign-in resume; exact Back-to-Search URL/control/result restoration; and pagination. Desktop **1280×800** and mobile **390×844** screenshots were inspected, with document and individual-card overflow assertions passing.

The original `listings.sql`, `assert_database.sql`, `sign-in.spec.ts`, and `identity-stack.spec.ts` are unchanged. GitHub Actions [passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46144370095) on **2026-11-28 (Asia/Colombo)** at evidence head **`244642187167bec34ef99ae13f79246ce736963d`**, containing implementation **`0b60d0664394d0e3a8790d693af858e1d7960507`**. The GitHub API confirmed the exact head, `status=completed` and `conclusion=success` before Phase 5 and roadmap completion were ticked. CI ran the same complete acceptance runner on Ubuntu 24.04, Python 3.14 and Node 24. All local and CI acceptance requirements passed.

## Sequential commit and CI closeout

Plan setup `f8db20aeafadf9e887cf07496ac9eededc9bbc82` was committed and pushed before implementation ([successful CI](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46141027192)). Every subphase's implementation/evidence commits were pushed and its CI success verified before starting the next.

| Subphase | Implementation | Evidence | Observed local Property / Engagement / standalone / stack counts | Verified CI |
| --- | --- | --- | --- | --- |
| 5.1 | `4f26793` | `0dbd828` | 28 / 9 / 11 / 5 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46141489016) |
| 5.2 | `e114ae7` | `5b60491` | 37 / 9 / 11 / 5 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46142226695) |
| 5.3 | `732a110` | `0913b60` | 37 / 9 / 14 / 6 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46143424358) |
| 5.4 | `0b60d06` | `2446421` | 37 / 9 / 14 / 7 | [Passed](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46144370095) |

Frontend lint/build/typecheck passed in every subphase. From 5.3 onward, the 14 standalone checks consist of the unchanged 11 OIDC cases plus three navigation/price-format checks. The final completion documentation is committed and pushed separately after the 5.4 local-plus-CI gate; its automatically triggered final CI run is verified before handing back.

## Implementation decisions

- `search-fixtures.ts` creates an isolated town namespace containing spaces and literal `%_!`. A verified seller uses the normal draft → encrypted private detail → authored showcase → explicit publish APIs for three listings; a fourth retains an authored showcase without publication. These runtime fixtures do not alter the Phase 1 SQL seed/assertions.
- `search-stack.spec.ts` exercises a signed-in buyer browser plus an independent fresh browser for listing-deep-link sign-in. It verifies exact query restoration through both search and listing return contexts, access modes, zero bedroom/parking values, public/private isolation, budget and cross-unit filters, pagination, and desktop/mobile rendering. No direct database fixture writes or authentication bypasses are used by this Compose test.
- Existing Playwright `*-stack.spec.ts` discovery and the complete `identity_acceptance.py` runner automatically include the new test. CI job/step names and the runner description now mention search. No additional grants, migrations or application changes are needed in this final subphase.
