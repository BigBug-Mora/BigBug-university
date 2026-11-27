# Phase 2.3 · Protected service calls

Prove that a receiving service can authenticate its caller and derive the acting EstateFlow account. Use Property as the first consumer so Phase 3 can reuse the same authentication dependency on listing routes.

[Phase 2](phase2.md) · [Cross-container rules](../../mvp/containers/containers.md#cross-container-rules) · [Property ownership](../../mvp/containers/property-service/property-service.md) · [Engagement resolver](phase2.1.md#internal-api-contract)

## Progress

- [ ] Reuse the shared JWT verifier in Property. Define a request-scoped actor containing the resolved EstateFlow UUID. Keep it separate from the caller identity and resource permission decisions.
- [ ] Use a distinct randomly generated shared secret per authorized connection for this phase, supplied in `X-EstateFlow-Service-Token` and compared in constant time. Configure separate Frontend-to-Property, Frontend-to-Engagement, and Property-to-Engagement credentials. Bind the accepted credentials to caller names and allowed routes in receiver configuration. Use fixture secrets for tests and keep real values in runtime configuration.
- [ ] Authenticate the caller and verify the user token at Property. Forward the original access token to Engagement using Property's own credential. Use a configured internal base URL with bounded timeouts. Accept the account UUID only from a successful, well-formed resolver response. Check status on each protected request through Engagement.
- [ ] Add an account-only diagnostic route in Property using the same dependency future listing routes will use. Preserve the public `/health` contract and update Property's image build context to include the shared package.
- [ ] Add Frontend and Engagement to local Compose with private service addresses. Make Frontend the browser entry point. Preserve the existing loopback-only Property health smoke check. Keep protected service traffic on a private network and document the encrypted transport and secret distribution required for hosting in Phase 17.
- [ ] Test the Property route with signed local identities, a fixture resolver for failure cases, and the real Engagement resolver for the integrated check.

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

Record the route test commands, built image results, and the actor dependency used by Phase 3. Record any contract change before handing off to Frontend and later services.
