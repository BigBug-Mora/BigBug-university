# Phase 2.4 · CI and shared Cognito acceptance

Run the browser and API acceptance checks against a clean local stack. Then repeat the sign-in path with the existing Cognito test users and shared RDS using the application's own app client.

[Phase 2](phase2.md) · [CI design](../../mvp/ci/cd/ci.md#github-actions-workflow) · [Phase 1.4 shared AWS evidence](../phase-01/phase1.4.md) · [Shared AWS runbook](../../../infra/runbooks/shared-aws-development.md) · [Cognito app client settings](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)

## Progress

- [x] Extend `.github/workflows/ci.yml` to install the pinned frontend and backend dependencies and run the 2.1–2.3 checks. Reuse disposable PostgreSQL and the existing migrations, fixture assertions, and Property health smoke. Run frontend lint, type checking, and the committed frontend test commands.
- [x] Build Frontend, Property, and Engagement in Compose. Run the browser acceptance flow against those images with a local test OIDC provider and JWKS. Use an issuer URL that resolves consistently from the browser and app containers. Have the test provider issue access tokens with the same claim shape the production verifier expects. Use the same Auth.js, verifier, resolver, and database paths as the live flow. Configure test issuers and credentials only in the test setup. Clean up the application and disposable database stacks on failure and success, and keep diagnostic output free of secrets.
- [x] Document exact local commands, supported configuration and ports, and expected results in the [frontend sign-in runbook](../../../infra/runbooks/frontend-sign-in.md#verify-the-complete-identity-stack). The Phase 1 startup and test instructions still apply.
- [x] Provision the dedicated confidential Auth.js app client in the shared Cognito pool. AWS CLI confirmed `estateflow-dev-authjs` (`5i4455r0g6va00qcqmhifid14s`) has a secret, the registered development callback and sign-out URLs, the authorization-code grant, scope `openid`, and Cognito-provided Managed Login branding (`350aba33-7912-4e47-a456-4e2f94f4da11`). The separate Phase 1 PKCE client remains available.
- [x] Review shared database access. Confirm the migration head, provision the dedicated Engagement runtime login and grants, and check that the running Engagement app can reach the existing SSM tunnel using the RDS CA bundle and full hostname verification. Document the tunnel address from the app's runtime environment. Apply any required reviewed migrations explicitly before starting the shared stack.
- [x] Record successful CI and live Cognito evidence below. Tick the phase plan and roadmap only after both checks pass.

## Acceptance check

### Disposable stack and CI

1. Start disposable PostgreSQL with `docker compose -p estateflow-db-test -f project/compose.test.yaml up -d --wait`. Apply Alembic and load the established Phase 1 fixtures. Apply the Engagement runtime-role grants using the documented setup.
2. Build and start the application with the test identity configuration. Start from a protected buyer fixture route while signed out and confirm sign-in resumes that destination. Use two distinct fictional identities to complete the browser callback, reach the protected view, compare account UUIDs, sign out, and sign back in. The first identity must retain its UUID and the second must have a different UUID.
3. Verify denial for missing or invalid credentials and a disabled account through Property. Confirm an unavailable resolver produces a service-failure response. Confirm all Phase 1 checks still pass. Run the same sequence in GitHub Actions and record the passing pull-request run.

### Shared Cognito and RDS

1. Start the documented RDS tunnel and stack using the dedicated Engagement login and Auth.js client. Confirm the frontend is using the shared Cognito issuer and approved local origin.
2. In a fresh browser session, sign in as the buyer through the app, reach the protected view, refresh, and record an anonymized account label. Check that browser-facing responses omit backend tokens. Sign out of the app and Cognito managed login and verify the protected page prompts for sign-in.
3. Sign in again as the buyer, then separately as the seller. Verify that the buyer UUID is stable and the seller UUID differs. Confirm the protected backend route denies an unverified request while the public health endpoint still returns 200. Stop the local stack and tunnel after the smoke test.

## Evidence to record

| Check | Evidence |
| --- | --- |
| Local disposable stack | On 2026-11-27 at revision `15e8cc7` (`codex/phase-2.4-ci-cognito-acceptance`), `npm run lint`, `npm run build`, `npm run typecheck`, and `npm run test:e2e` (11 Playwright fixture tests) passed in `project/frontend`. `python project/tests/integration/identity_acceptance.py` passed from a clean disposable PostgreSQL 17 container: applied `0001 (head)`, provisioned `estateflow_engagement` and ran `grant-engagement-runtime.sql`, loaded `listings.sql` and passed `assert_database.sql`, re-verified `0001 (head)` on repeat upgrade, passed 7 Property tests and 9 Engagement tests, built the `estateflow-identity-test` Compose images, and passed `tests/identity-stack.spec.ts` (Property `/health` 200 and 401 denials, buyer listing return, refresh `no-store`, expiry-only `/api/auth/session`, managed logout, repeat buyer UUID stability, distinct seller UUID, disabled account 403 denial, and stopped `engagement-service` 503 failure), then removed all containers and the network. |
| Pull request | [Pull request #6](https://github.com/BigBug-Mora/BigBug-university/pull/6) passed workflow `EstateFlow CI` / job `Database and Property smoke checks` on commit `15e8cc7550140509a6ef8e0c528370ff176ac5dd`: [Run 46031419605](https://github.com/BigBug-Mora/BigBug-university/actions/runs/46031419605) (2m38s). |
| Shared smoke | On 2026-11-27 at revision `15e8cc7`, verified `0001 (head)` on `estateflow-postgres-dev` (PostgreSQL `17.12`, private, encrypted) through the SSM tunnel (`127.0.0.1:15432` → RDS `5432`; Docker container `host.docker.internal` resolved to `192.168.65.254` with `sslmode=verify-full` and `/rds-ca.pem`). Provisioned `estateflow_engagement` on `estateflow_app` with `infra/aws/grant-engagement-runtime.sql`; confirmed `pg_stat_ssl = ('estateflow_engagement', True)` inside `engagement-service` and `InsufficientPrivilege` on `CREATE TABLE public.*` and `SELECT` from `property.listings`. Verified `estateflow-dev-authjs` (`5i4455r0g6va00qcqmhifid14s`, Managed Login branding `350aba33-7912-4e47-a456-4e2f94f4da11`, 60-minute access/ID tokens, 1-day refresh token) and Auth.js `8`-hour max session (reauthentication on access token expiry). Against the live `estateflow-identity-live` Compose stack (`AUTH_URL=http://localhost:3000`, `ESTATEFLOW_COGNITO_ISSUER=https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_ph4m9qYyu`, `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER=0`): buyer (`buyer-smoke`, anonymized) signed in from `/buyer/listings/courtyard-house`, kept the same UUID across refresh (`Cache-Control: no-store`) and repeat sign-in after Cognito `/logout` (which cleared `/api/auth/session` to `null` and forced sign-in on revisit), confirmed `/api/auth/session` contained only `expires` within the 60-minute lifetime and HTML omitted server secrets, and seller (`seller-smoke`, anonymized) resolved to a distinct UUID on `/seller/workspace` and signed out cleanly. `account.accounts` on RDS confirmed 2 active rows with 2 distinct subjects and 2 distinct UUIDs under the shared Cognito issuer. Loopback `http://127.0.0.1:8000/internal/identity/me` returned `401` without credentials and with `Authorization: Bearer invalid`, while `GET /health` returned `200 {"status":"ok"}`. Stopped the Compose stack and terminated the SSM session afterward. |
| Handoff | Runtime role `estateflow_engagement` on `estateflow_app` (`RDS_ENGAGEMENT_PASSWORD` in ignored `.env.rds-admin`). Cognito client `estateflow-dev-authjs` (`5i4455r0g6va00qcqmhifid14s`, Managed Login branding `350aba33-7912-4e47-a456-4e2f94f4da11`). Local ignored files retained: `.env.rds-admin`, `project/.env.identity`, `project/ap-south-1-bundle.pem`. Startup commands in [the shared Cognito/RDS runbook section](../../../infra/runbooks/frontend-sign-in.md#verify-shared-cognito-and-rds). Phase 3 builds seller draft ownership on `ActorAuthentication` (`project/services/property/actor.py`). |

### Verification notes

- Earlier on 2026-11-27, the shared RDS connection timed out through SSM because `estateflow-tunnel` (`sg-038c85f1b1c26cd5f`) had no outbound rules. After the owner restored TCP 5432 egress to `estateflow-db` (`sg-0ede08736c4876e05`) and TCP 443 egress to `0.0.0.0/0`, the tunnel and `engagement-service` TLS checks succeeded.
- Cognito Managed Login v2 on domain `ap-south-1ph4m9qyyu.auth.ap-south-1.amazoncognito.com` initially displayed "Login pages unavailable" for `estateflow-dev-authjs` because CLI-created app clients do not receive a default branding style; creating Cognito-provided branding (`UseCognitoProvidedValues: true`) resolved it and is documented in the [frontend sign-in runbook](../../../infra/runbooks/frontend-sign-in.md#verify-shared-cognito-and-rds).

### Phase 2.1 resolver verification

Run from the repository root in PowerShell with the project virtual environment active and a fresh disposable database. The sample credentials below are for the disposable database.

```powershell
python -m pip install -r project/requirements.txt -r project/services/engagement/tests/requirements.txt
python -m pip check
$composeFile = 'project/compose.test.yaml'
docker compose -p estateflow-db-test -f $composeFile up -d --wait
$env:ESTATEFLOW_DATABASE_URL = 'postgresql+psycopg://estateflow_migrator:disposable-migration@127.0.0.1:55432/estateflow_test'
python -m alembic -c project/alembic.ini upgrade head
Get-Content -Raw infra/aws/provision-engagement-runtime.sql | docker compose -p estateflow-db-test -f $composeFile exec -T db psql -X -U postgres -d estateflow_test -v ON_ERROR_STOP=1
docker compose -p estateflow-db-test -f $composeFile exec -T db psql -X -U postgres -d estateflow_test -v ON_ERROR_STOP=1 -c "ALTER ROLE estateflow_engagement PASSWORD 'disposable-engagement'" -c 'REVOKE CONNECT, TEMPORARY ON DATABASE estateflow_test FROM PUBLIC'
Get-Content -Raw infra/aws/grant-engagement-runtime.sql | docker compose -p estateflow-db-test -f $composeFile exec -T db psql -X -U estateflow_migrator -d estateflow_test -v ON_ERROR_STOP=1
docker compose -p estateflow-db-test -f $composeFile exec -T db psql -X -U estateflow_migrator -d estateflow_test -v ON_ERROR_STOP=1 -f /fixtures/listings.sql -f /checks/assert_database.sql
$env:ESTATEFLOW_TEST_ENGAGEMENT_DATABASE_URL = 'postgresql://estateflow_engagement:disposable-engagement@127.0.0.1:55432/estateflow_test'
$env:ESTATEFLOW_TEST_MIGRATOR_DATABASE_URL = 'postgresql://estateflow_migrator:disposable-migration@127.0.0.1:55432/estateflow_test'
python -W error::ResourceWarning -m unittest discover -s project/services/engagement/tests -v
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
docker build -f project/services/engagement/Dockerfile -t estateflow-phase21-engagement project
docker compose -p estateflow-db-test -f $composeFile down
```
