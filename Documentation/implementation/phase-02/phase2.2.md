# Phase 2.2 · Frontend sign-in and session

Build the smallest Next.js application that exercises Auth.js sign-in, a protected view, and sign-out. Test against a local OIDC provider and fixture API responses while the services are under development.

[Phase 2](phase2.md) · [Frontend design](../../mvp/containers/frontend/frontend.md) · [MVP technology stack](../../mvp/teach-stack/tech-stack.md#1-technology-stack) · [Auth.js Cognito provider](https://authjs.dev/reference/core/providers/cognito)

## Progress

- [x] Scaffold the Next.js app and checked-in dependency lockfile under `project/frontend/`. Add its Dockerfile, server configuration, and one public landing page with buyer and seller sign-in entry points. Use minimal protected destinations to verify each entry. Use the app router and keep Auth.js provider configuration server-side.
- [x] Configure Auth.js for Cognito managed login using the authorization-code flow. Verify the provider's state and PKCE checks, app client and issuer settings, and exact registered callback. Request the minimum scopes needed for sign-in. Treat the Cognito client secret and Auth.js secret as runtime server configuration.
- [x] Keep the Cognito access token and expiration in Auth.js protected session state accessible to server-side code. Keep the client-visible session minimal. Call the Engagement resolver from the server as part of sign-in completion before showing the signed-in state. Render the protected view with a server-side Property call for verification in [2.3](phase2.3.md).
- [x] Require a verified session before buyer search or listing access. Validate return destinations against the app's own allowed routes. For buyers, resume the search page or the same linked listing. For sellers, return to the protected workspace. Use a safe fallback for missing or invalid destinations. Use fixture destinations to verify the routing contract ahead of Phases 4 and 5.
- [x] Handle signed-out, expired session, permission denied, and temporarily unavailable states. On expiration, start a fresh authorization flow when the user signs in again. Sign-out clears the application session and redirects through Cognito managed logout to the registered app URL. Keep protected responses out of shared caches.
- [x] Add a local sign-in runbook section with example configuration keys, callback and sign-out URLs, and clean restart instructions. Use the existing Cognito pool with a dedicated confidential app client during [2.4](phase2.4.md). [Cognito managed logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html)

## Acceptance check

Start Next.js, a local test OIDC provider, and fixture implementations of the service contracts. Run the browser checks once against these fixtures and again against the real backend stack in [2.4](phase2.4.md).

1. Visit the public page while signed out. Open the protected page and complete sign-in. Verify the browser returns to the intended view and a refresh preserves access.
2. Sign out and revisit the protected page. Verify it prompts for sign-in. Exercise expiry and a canceled sign-in and confirm each has a recovery path.
3. Open a test buyer search route and a test listing deep link while signed out. Verify each prompts for sign-in before returning any listing data. Complete sign-in and verify the browser resumes the intended destination. Exercise an invalid return destination and confirm navigation stays within the app. Check that the client-visible session and browser-facing API responses omit access tokens and service credentials.
4. Verify a disabled account shows a forbidden state and an unavailable backend shows a recoverable service failure.

## Evidence

Verified locally on 2026-11-27 on `codex/phase-2.2-frontend-sign-in`. [Frontend verification commands](../../../infra/runbooks/frontend-sign-in.md#verify-with-local-fixtures)

| Check | Result |
| --- | --- |
| Frontend lint, build, and type check | `npm run lint`, `npm run build`, and `npm run typecheck` passed. |
| Browser acceptance | `npm run test:e2e` passed all 11 tests against the standalone Next.js build, local OIDC provider, and Engagement fixture. The tests exercised buyer and seller entry, refresh, managed logout, listing return, unsafe destination fallback, canceled sign-in, state mismatch, expiry, denied accounts, and service failure and recovery. |
| Frontend container | `docker build -t estateflow-frontend:phase22 project/frontend` passed from the repository root. The running image served the landing page and bundled CSS and redirected signed-out buyer requests to the no-store sign-in page. |
| Backend regression | All nine Engagement tests and the Property health test passed. PostgreSQL 17 migrated to `0001 (head)` and passed the Phase 1 fixture assertions. |

### Session and routing decisions

- The App Router uses Auth.js with the Cognito provider, authorization-code flow, S256 PKCE, state and nonce verification, confidential client authentication, and the `openid` scope. The callback is `/api/auth/callback/cognito`. [Frontend runbook](../../../infra/runbooks/frontend-sign-in.md)
- The Auth.js encrypted, HTTP-only session cookie contains the access token and provider expiration. Server code reads it from the cookie, checks expiration on every protected request, and calls Engagement with the original access token and the Frontend service credential. The browser session endpoint returns only the effective expiration. Sign-in sends `prompt=login` so Cognito managed login requests credentials again even when its browser session is still active. [Cognito authorization endpoint](https://docs.aws.amazon.com/cognito/latest/developerguide/authorization-endpoint.html#authorization-endpoint-request-parameters)
- Engagement must resolve an active account before Auth.js issues a session. The frontend guard rechecks account status on protected requests and denies access when verification fails. The current protected view displays the verified account UUID. Phase 2.3 replaces the view's protected account lookup with Property's account-only route and retains Engagement resolution during sign-in completion.
- The guard resumes `/buyer/search`, `/buyer/listings/<id>`, or `/seller/workspace`. Listing IDs are a single ASCII segment of up to 64 letters, digits, and hyphens, starting with a letter or digit. Return destinations use the configured app origin and the same route allowlist on sign-in and callback. An invalid destination falls back to buyer search. Phases 4, 5, and 11 can reuse the guard as they add listing and search behavior.
- Sign-out clears the Auth.js cookie and opens Cognito managed logout, which returns to the registered application root. Protected responses and backend account lookups use no-store caching.
