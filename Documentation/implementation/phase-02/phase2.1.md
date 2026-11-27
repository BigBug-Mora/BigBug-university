# Phase 2.1 · Verified identity and account mapping

Add the Engagement account module, PostgreSQL access, and shared Cognito verifier. Exercise the real FastAPI route against disposable PostgreSQL before adding browser sign-in.

[Phase 2](phase2.md) · [Account schema](../../mvp/database/schema.md) · [Database ownership and authorization](../../mvp/database/contracts.md#ownership-and-authorization) · [AWS Cognito token verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)

## Progress

- [x] Add the Engagement FastAPI app and image under `project/services/engagement/`. Place the resolver and database access in its account module. Add the reusable Cognito verifier and internal caller authentication under `project/shared/`.
- [x] Verify bearer access tokens using a maintained JWT library. Require a valid RS256 signature from the configured issuer's JWKS, exact issuer, expected app-client ID in `client_id`, `token_use=access`, a nonempty subject, and a valid expiration. Honor `nbf` when present. Pin the issuer and key URL in trusted configuration. Cache keys, bound timeouts and refresh on rotation, and fail closed when a key cannot be established.
- [x] In one database transaction, insert a first-seen account using the issuer and subject uniqueness constraint. On conflict, select the winning row and check its current status. Return its existing UUID only after a successful commit. Cover concurrent first use, retries, and disabled rows. Create the account record on first authenticated use. Leave optional profile creation for a feature that collects a display name.
- [x] Reuse `0001` and its account tables. Add reviewed SQL and setup steps for a dedicated Engagement runtime login with connection, schema usage, and the minimum account-table permissions for lookup and insert. Apply grants after migrations and exercise the same grants on disposable PostgreSQL. Keep migration ownership and role provisioning separate.
- [x] Package Engagement with the shared module using the common `project/` build context. Add PostgreSQL integration tests and a deterministic JWKS fixture with signed buyer and seller tokens. Confirm both HTTP behavior and committed database state.

## Internal API contract

- `POST /internal/accounts/resolve` takes a Cognito access token in `Authorization: Bearer …` and an internal credential in `X-EstateFlow-Service-Token`. The route accepts calls from Frontend and Property with their own credentials and derives the identity from the verified token. The request needs no body.
- Return HTTP 200 and `{"account_id":"<uuid>"}` after an active account is resolved. Missing or invalid credentials return 401. A recognized caller lacking permission for this route or a disabled account returns 403. A transient database or verification dependency failure returns 503 when the service cannot reach an authorization decision. Errors and logs omit token claims and credentials. Mark responses non-cacheable.
- Keep raw tokens and passwords out of database rows and request logs. Authenticate the caller before bearer verification or database work. Configure separate credentials per caller and receiver as defined in [2.3](phase2.3.md).

## Acceptance check

Start `project/compose.test.yaml` under the existing disposable Compose project, apply Alembic to head, and provision the scoped runtime role. Run the Engagement route tests against the disposable database through that role. Record the exact test command in [2.4](phase2.4.md).

| Scenario | Expected result |
| --- | --- |
| First and returning identity, including concurrent initial requests | Exactly one account row and the same UUID in every successful response. |
| Two different subjects, or the same subject under separately configured test issuers | Separate UUIDs. A token from an issuer outside the active configuration is rejected. |
| Missing, malformed, expired, wrong-issuer, wrong-client, or wrong-token-type credential, or invalid signature | HTTP 401 and no account created. |
| Rotated key and verifier dependency failure | A valid new key is accepted after refresh. A failed key lookup with no usable cache fails closed. |
| Disabled account or unavailable database | HTTP 403 or 503 respectively, with the existing row preserved. |
| Runtime login probes | Account lookup and insertion succeed. Schema creation and unrelated schema access are denied. |

## Evidence

Local verification passed on 2026-11-27 on `codex/phase-2.1-account-mapping`. See [reproduction commands](phase2.4.md#phase-21-resolver-verification).

| Check | Result |
| --- | --- |
| Disposable PostgreSQL 17 | Applied `0001`, provisioned the scoped runtime login, loaded fixtures, ran the Phase 1 SQL assertions, and verified `0001 (head)` after a repeat upgrade. |
| Engagement integration suite | All nine tests passed. Eight concurrent requests for a first-seen identity returned the same UUID and committed one active row. The suite verified identity separation, caller and bearer denials, rotation, dependency failures, disabled accounts, and denied runtime privileges. |
| Engagement image | Built from `project/` and used its default command. Loopback HTTP returned 401 without credentials, the same UUID for the buyer through both configured callers, and a different UUID for the seller. The container used disposable PostgreSQL and a local signing-key fixture. |
| Property regression | The existing Property test passed. The built image returned HTTP 200 and `{"status":"ok"}` at `/health`. |

### Runtime and handoff

Build from the repository root with `docker build -f project/services/engagement/Dockerfile -t estateflow-phase21-engagement project`. The image runs the Engagement app factory on port 8000. Supply these settings at runtime.

| Setting | Value |
| --- | --- |
| `ESTATEFLOW_ENGAGEMENT_DATABASE_URL` | libpq PostgreSQL URL or connection string for the scoped `estateflow_engagement` login. [Database setup](../../../infra/runbooks/shared-aws-development.md#engagement-runtime-login) |
| `ESTATEFLOW_COGNITO_ISSUER` | Exact user-pool issuer, without a trailing slash. The verifier loads `/.well-known/jwks.json` under this issuer and requires HTTPS by default. |
| `ESTATEFLOW_COGNITO_CLIENT_ID` | App client ID expected in the access token's `client_id` claim. |
| `ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN` | Secret shared with Frontend for calls to Engagement. |
| `ESTATEFLOW_PROPERTY_TO_ENGAGEMENT_TOKEN` | Separate secret shared with Property for calls to Engagement. |
| `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER` | Set to `1` only with the local test identity provider. |

The verifier caches a key set for up to five minutes and refreshes on an unknown key ID. A refresh after initial population or a failed fetch starts a five-second cooldown. A JWKS failure returns 503 when the request cannot use a cached key. The database transaction uses READ COMMITTED so a second statement can see the winning committed account after a conflicting insert. Profile creation remains with the first feature that collects a display name.

Phase 2.2 can use the documented resolver directly. Phase 2.3 can reuse `CognitoVerifier.verify_bearer` from `project/shared/cognito.py` and `ServiceAuthenticator` from `project/shared/service_auth.py`. Compose integration belongs to 2.3. The CI workflow and shared AWS exercise belong to 2.4.
