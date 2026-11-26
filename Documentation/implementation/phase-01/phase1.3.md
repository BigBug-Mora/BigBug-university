# Phase 1.3 · Continuous integration

Run the starter application and migration checks on every pull request and push to `main`. Reuse the documented local checks so a teammate can reproduce a failure from the runner. [Phase 1](phase1.md) · [CI design](../../mvp/ci/cd/ci.md)

## Progress

- [x] Add [the CI workflow](../../../.github/workflows/ci.yml) using the pinned Python dependencies and the disposable PostgreSQL 17 stack from [Phase 1.2](phase1.2.md).
- [x] Apply migrations, load fictional fixtures, run database assertions and the [starter API test](phase1.1.md), and build and smoke-test the Property image. The workflow commands passed locally.
- [x] Name the check `Database and Property smoke checks` and record the branch protection handoff below.
- [ ] Record reproducible commands and the CI run that verifies the phase. Add later frontend, integration, and packaging checks when those components land.

## Acceptance check

Open a pull request. The workflow must start a clean database, apply migrations, run fixture and starter checks, and publish a passing result using runner-local test credentials. Record the run link. Confirm that the checks are required on `main` or record the outstanding repository-owner action.

## Verification

Reproduce the workflow from the repository root using the [service test](../../../README.md#run-the-service-test), [disposable database](../../../README.md#verify-the-disposable-database), and [Compose startup](../../../README.md#run-with-docker-compose) instructions. The [workflow](../../../.github/workflows/ci.yml) contains the exact runner commands.

- On 2026-11-26, `python -m pip check` reported no broken requirements. The disposable database applied revision `0001`, loaded the fixtures, passed the SQL assertions, and reported `0001 (head)` after a second upgrade. The Property API test passed and the built image returned HTTP 200 with `{"status":"ok"}` through the published port. Both Compose test projects were removed afterward.

## Repository owner handoff

GitHub Actions is enabled. GitHub returned HTTP 403 for both branch protection and branch rules because the current plan does not support those features for this private repository. When branch protection is available, the owner of `BigBug-Mora/BigBug-university` can open **Settings → Branches**, edit or add the rule matching `main`, select **Require status checks to pass before merging**, and require `Database and Property smoke checks` from GitHub Actions. [GitHub branch protection settings](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

## Decision log

- CI uses disposable PostgreSQL and fictional fixtures. Live AWS and model checks are explicit integration runs.
- Keep one required check for the foundation workflow and give each verification step its own name. Use the existing Compose files so local and CI checks exercise the same database bootstrap and image startup.
