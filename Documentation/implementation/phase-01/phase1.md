# Phase 1 · Development foundation

After this phase, a teammate can clone the repo, run a small application smoke check, migrate and seed a disposable PostgreSQL instance, and see those checks pass in GitHub Actions. The team can also confirm access to the same private RDS, S3, and Cognito resources from two development machines. [Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md)

Phase 1.1 established a thin Property service with `project/main.py` as the local entry point. Phase 1.2 packaged the MVP PostgreSQL DDL as an Alembic migration and verified it with disposable fixtures. Domain behavior follows in later phases. [Database schema](../../mvp/database/schema.md) · [Technology stack](../../mvp/teach-stack/tech-stack.md) · [CI design](../../mvp/ci/cd/ci.md)

## Progress

- [x] [Phase 1.1 · Runnable development foundation](phase1.1.md)
- [x] [Phase 1.2 · Versioned database and fixtures](phase1.2.md)
- [x] [Phase 1.3 · Continuous integration](phase1.3.md)
- [x] [Phase 1.1 · Runnable development foundation](phase1.1.md)
- [x] [Phase 1.2 · Versioned database and fixtures](phase1.2.md)
- [x] [Phase 1.3 · Continuous integration](phase1.3.md)
- [x] [Phase 1.4 · Shared AWS development](phase1.4.md)
- [x] Record Phase 1 acceptance evidence and tick the roadmap.

## Execution order

Start with 1.1. At the beginning of 1.2, confirm a PostgreSQL major version with the AWS environment work in 1.4, so disposable tests and RDS use the same major. 1.3 consumes the migration and fixture commands from 1.2. AWS resource and access setup can proceed alongside local work once the intended account and region are known. Run the shared migration only after 1.2 has passed locally and the team has chosen the person and window for applying it.

## Acceptance

1. From a clean checkout, run the documented local startup and smoke commands. The starter API returns the expected health response. No cloud credentials are needed for this smoke check.
2. Bring up the disposable PostgreSQL instance, apply committed migrations, seed fictional data, and run assertions for House, Apartment, and Land. Running the migration command again succeeds with no pending migrations.
3. Open a pull request and record the successful CI run for migrations, fixtures, and the starter application check.
4. Record successful managed-service smoke checks from the shared development setup (owner's machine using the shared `estateflow-dev` IAM profile; separate second-teammate machine check waived per owner decision on 2026-11-27). Reach the private database through the tunnel, verify Cognito test-user sign-ins, and read the authorized S3 fixture. Record results without credentials or private values.

## Decision log

- Start with one thin Property API smoke path and disposable PostgreSQL. Apply the shared database migrations through an explicit step. Build the remaining containers as their first features land.
- Use the MVP schema and contracts as the baseline. If implementation reveals an unresolved rule, record the finding and its effect here. Update the relevant design document in `Documentation/` when the rule is resolved and the design changes.
- On 2026-11-27, the owner standardized on a single shared `Estateflow` IAM identity (`estateflow-dev`) and waived the two-teammate machine check for Phase 1.4 acceptance. See [Phase 1.4](phase1.4.md#decision-log).

## Discoveries and handoff

Phase 1.3 reused the [verified starter commands](phase1.1.md#verification-and-ci-handoff) and the [verified PostgreSQL 17 commands](phase1.2.md#verification-and-ci-handoff) and passed on [Pull request #2](https://github.com/BigBug-Mora/BigBug-university/pull/2). Phase 1.4 provisioned PostgreSQL 17.12 RDS (`estateflow-postgres-dev`), EC2 SSM tunnel (`estateflow-tunnel`), private S3 bucket (`estateflow-dev-photos-bigbug-mumbai`), and Cognito user pool with buyer/seller test accounts in `ap-south-1`, applied revision `0001`, and passed all owner-machine smoke checks on 2026-11-27.
