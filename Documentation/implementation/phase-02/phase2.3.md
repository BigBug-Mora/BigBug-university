# Phase 2.3 · Protected service calls

Prove that a receiving service can authenticate its caller and derive the acting EstateFlow account. Use Property as the first consumer so Phase 3 can reuse the same authentication dependency on listing routes.

[Phase 2](phase2.md) · [Cross-container rules](../../mvp/containers/containers.md#cross-container-rules) · [Property ownership](../../mvp/containers/property-service/property-service.md) · [Engagement resolver](phase2.1.md#internal-api-contract)

## Progress

- [x] Reuse the shared JWT verifier in Property. Define a request-scoped actor containing the resolved EstateFlow UUID. Keep it separate from the caller identity and resource permission decisions.
- [x] Use a distinct randomly generated shared secret per authorized connection for this phase, supplied in `X-EstateFlow-Service-Token` and compared in constant time. Configure separate Frontend-to-Property, Frontend-to-Engagement, and Property-to-Engagement credentials. Bind the accepted credentials to caller names and allowed routes in receiver configuration. Use fixture secrets for tests and keep real values in runtime configuration.
- [x] Authenticate the caller and verify the user token at Property. Forward the original access token to Engagement using Property's own credential. Use a configured internal base URL with bounded timeouts. Accept the account UUID only from a successful, well-formed resolver response. Check status on each protected request through Engagement.
- [x] Add an account-only diagnostic route in Property using the same dependency future listing routes will use. Preserve the public `/health` contract and update Property's image build context to include the shared package.
- [x] Add Frontend and Engagement to local Compose with private service addresses. Make Frontend the browser entry point. Preserve the existing loopback-only Property health smoke check. Keep protected service traffic on a private network and document the encrypted transport and secret distribution required for hosting in Phase 17.
- [x] Test the Property route with signed local identities, a fixture resolver for failure cases, and the real Engagement resolver for the integrated check.

## Protected API contract

- `GET /internal/identity/me` expects the Frontend service credential and the Cognito bearer access token. It returns HTTP 200 and `{"account_id":"<uuid>"}` with no protected-resource data. Responses are non-cacheable. Use the result in the protected frontend smoke view.
- Missing or invalid service or user credentials return HTTP 401. A recognized but unauthorized caller or a disabled account returns 403. If the resolver is unavailable or returns an unusable response, return 503. Never accept an account ID, role, or caller name asserted by the browser as authority.
- Property derives the actor on the server. Phase 3 and later handlers add resource authorization where each resource is owned. Keep the diagnostic route internal as those features land.

## Acceptance check

Run Property with the local JWKS fixture. Exercise the protected route both with a fixture resolver and with the Engagement image from [2.1](phase2.1.md) connected to disposable PostgreSQL. Check these cases through HTTP.

| Request | Expected result |
| --- | --- |
| Correct Frontend credential and valid access token for each test identity | HTTP 200 and the corresponding Engagement UUID. The two UUIDs differ. |
| Valid token with a missing, wrong, or differently scoped internal credential | HTTP 401 or 403 according to whether the caller is authenticated. |
| Valid caller with missing or rejected token | HTTP 401. An asserted account ID cannot authenticate a request or override the verified actor. |
| Valid caller and token for a disabled account | HTTP 403 even if a previous request in the same user session succeeded. |
| Resolver outage or invalid response | HTTP 503 with no actor data. |
| Unauthenticated `GET /health` | HTTP 200 and `{"status":"ok"}`. |

## Evidence

Verified locally on 2026-11-27 on `codex/phase-2.3-protected-service-calls`.

| Check | Result |
| --- | --- |
| Property HTTP tests | `python -W error::ResourceWarning -m unittest discover -s project/services/property/tests -v` passed all seven tests. Covered credential denials, original bearer forwarding, disabled accounts, dependency failures, malformed responses, and public health. |
| Engagement and PostgreSQL regressions | All nine [Engagement tests](phase2.4.md#phase-21-resolver-verification) passed with the scoped role. Disposable PostgreSQL 17 passed fixture assertions and remained at `0001 (head)` after a repeat upgrade. |
| Frontend | `npm run lint`, `npm run build`, `npm run typecheck`, and all 11 Playwright tests passed with the local provider and API fixtures. The browser suite exercised a Property-only outage and recovery. |
| Built images | Frontend, Property, and Engagement built and started in Compose. The image check below confirmed two distinct account UUIDs matched Engagement, a disabled account lost access, and invalid credentials were denied. Property returned the original health response, and the frontend redirected signed-out requests to sign-in. |
| Direct launch | `python project/main.py` served the original Property health response without identity settings. |

### Reproduce the image check

Use the disposable database and role setup from [2.4](phase2.4.md#phase-21-resolver-verification), with `estateflow-phase23` as the project name. Keep the database running until this check finishes. The commands below use PowerShell from the repository root with fictional credentials.

```powershell
$env:AUTH_SECRET = 'estateflow-fixture-session-secret'
$env:ESTATEFLOW_COGNITO_ISSUER = 'http://identity-fixture:47122/pool'
$env:ESTATEFLOW_COGNITO_CLIENT_ID = 'estateflow-test-client'
$env:ESTATEFLOW_COGNITO_CLIENT_SECRET = 'estateflow-fixture-client-secret'
$env:ESTATEFLOW_COGNITO_LOGIN_ORIGIN = 'http://identity-fixture:47122'
$env:ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER = '1'
$env:ESTATEFLOW_ENGAGEMENT_BASE_URL = 'http://engagement-service:8000'
$env:ESTATEFLOW_ENGAGEMENT_DATABASE_URL = 'postgresql://estateflow_engagement:disposable-engagement@db:5432/estateflow_test'
$env:ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN = 'fixture-frontend-to-engagement'
$env:ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN = 'fixture-frontend-to-property'
$env:ESTATEFLOW_PROPERTY_TO_ENGAGEMENT_TOKEN = 'fixture-property-to-engagement'
$stack = @('-p', 'estateflow-phase23', '-f', 'project/compose.yaml', '-f', 'project/compose.test.yaml', '--profile', 'identity')
docker compose @stack up --build --detach --wait --force-recreate property-service engagement-service frontend
docker run --rm --network estateflow-phase23_default --network-alias identity-fixture `
  --mount "type=bind,source=$PWD/project/tests,target=/app/project/tests,readonly" `
  -e ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN -e ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN `
  estateflow-phase23-engagement-service python -m unittest -v project.tests.integration.property_identity_smoke
curl.exe --fail http://127.0.0.1:8000/health
curl.exe --fail http://localhost:3000/ -o NUL
docker compose @stack down
```

The test process serves JWKS on the Compose network and runs the API acceptance checks with two distinct subjects. The browser fixture check runs separately using the [frontend runbook](../../../infra/runbooks/frontend-sign-in.md#verify-with-local-fixtures).

### Service decisions

- Protected Property handlers use `ActorAuthentication.require` in a FastAPI dependency with the route's caller allowlist. This dependency resolves an `Actor` carrying the EstateFlow account UUID. Resource permissions remain the responsibility of each handler.
- Property forwards the original bearer to the configured Engagement origin. It uses two-second socket timeouts, rejects redirects, limits the response body to 4 KiB, and requires a UUID in the resolver's HTTP 200 response. Engagement's 403 is passed through as a generic 403. Other unexpected upstream statuses, including an upstream 401 after local bearer verification, return 503.
- The Auth.js callback continues resolving accounts through Engagement. The frontend's protected views use the Property route and recheck account status on each protected request. [Runtime setup](../../../infra/runbooks/frontend-sign-in.md#run-the-identity-stack-with-compose)
