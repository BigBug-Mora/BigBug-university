# Phase 1 · Development foundation

After this phase, a teammate can clone the repo, run a small application smoke check, migrate and seed a disposable PostgreSQL instance, and see those checks pass in GitHub Actions. The team can also confirm access to the same private RDS, S3, and Cognito resources from two development machines. [Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md)

The starting repository has empty `project/main.py` and `project/requirements.txt` files. The initial PostgreSQL DDL lives in Markdown. Start with a thin service and test harness, then add the domain behavior in later phases. [Database schema](../../mvp/database/schema.md) · [Technology stack](../../mvp/teach-stack/tech-stack.md) · [CI design](../../mvp/ci/cd/ci.md)

## Progress

- [ ] [Phase 1.1 · Runnable development foundation](phase1.1.md)
- [ ] [Phase 1.2 · Versioned database and fixtures](phase1.2.md)
- [ ] [Phase 1.3 · Continuous integration](phase1.3.md)
- [ ] [Phase 1.4 · Shared AWS development](phase1.4.md)
- [ ] Record Phase 1 acceptance evidence and tick the roadmap.

## Execution order

Start with 1.1. At the beginning of 1.2, confirm a PostgreSQL major version with the AWS environment work in 1.4, so disposable tests and RDS use the same major. 1.3 consumes the migration and fixture commands from 1.2. AWS resource and access setup can proceed alongside local work once the intended account and region are known. Run the shared migration only after 1.2 has passed locally and the team has chosen the person and window for applying it.

## Acceptance

1. From a clean checkout, run the documented local startup and smoke commands. The starter API returns the expected health response. No cloud credentials are needed for this smoke check.
2. Bring up the disposable PostgreSQL instance, apply committed migrations, seed fictional data, and run assertions for House, Apartment, and Land. Running the migration command again succeeds with no pending migrations.
3. Open a pull request and record the successful CI run for migrations, fixtures, and the starter application check.
4. Record successful managed-service smoke checks from two development machines. Both must reach the same private database through the tunnel, verify a Cognito test-user sign-in, and read the same authorized S3 fixture. Record results without credentials or private values.

## Decision log

- Start with one thin Property API smoke path and disposable PostgreSQL. Apply the shared database migrations through an explicit step. Build the remaining containers as their first features land.
- Use the MVP schema and contracts as the baseline. If implementation reveals an unresolved rule, record the finding and its effect here. Update the relevant design document in `Documentation/` when the rule is resolved and the design changes.

## Discoveries and handoff

Add the chosen versions, verified commands, relevant test output, and links to CI evidence as the work lands. Record any remaining dependency with its owning phase before handing off to Phase 2.
