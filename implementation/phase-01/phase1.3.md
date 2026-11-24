# Phase 1.3 · Continuous integration

Run the starter application and migration checks on every pull request and push to `main`. Reuse the documented local checks so a teammate can reproduce a failure from the runner. [Phase 1](phase1.md) · [CI design](../../Documentation/mvp/ci/cd/ci.md)

## Progress

- [ ] Add `.github/workflows/ci.yml` after [the initial migration](phase1.2.md) is ready. Configure a disposable PostgreSQL instance of the same major version as RDS and install the pinned Python dependencies.
- [ ] Apply the migrations, load fictional fixtures, run database assertions, and run the [starter API test](phase1.1.md). Build and smoke-test the starter image after its Dockerfile is available.
- [ ] Give the checks clear names and enable the required checks for `main` with the repository owner. If the setting cannot be applied with current access, record the exact setting and owner in the phase handoff.
- [ ] Record reproducible commands and the CI run that verifies the phase. Add later frontend, integration, and packaging checks when those components land.

## Acceptance check

Open a pull request. The workflow must start a clean database, apply migrations, run fixture and starter checks, and publish a passing result using runner-local test credentials. Record the run link. Confirm that the checks are required on `main` or record the outstanding repository-owner action.

## Decision log

- CI uses disposable PostgreSQL and fictional fixtures. Live AWS and model checks are explicit integration runs.
