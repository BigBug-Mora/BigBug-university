# Phase 2.2 · Frontend sign-in and session

Build the smallest Next.js application that exercises Auth.js sign-in, a protected view, and sign-out. Test against a local OIDC provider and fixture API responses while the services are under development.

[Phase 2](phase2.md) · [Frontend design](../../mvp/containers/frontend/frontend.md) · [MVP technology stack](../../mvp/teach-stack/tech-stack.md#1-technology-stack) · [Auth.js Cognito provider](https://authjs.dev/reference/core/providers/cognito)

## Progress

- [ ] Scaffold the Next.js app and checked-in dependency lockfile under `project/frontend/`. Add its Dockerfile, server configuration, and one public landing page with buyer and seller sign-in entry points. Use minimal protected destinations to verify each entry. Use the app router and keep Auth.js provider configuration server-side.
- [ ] Configure Auth.js for Cognito managed login using the authorization-code flow. Verify the provider's state and PKCE checks, app client and issuer settings, and exact registered callback. Request the minimum scopes needed for sign-in. Treat the Cognito client secret and Auth.js secret as runtime server configuration.
- [ ] Keep the Cognito access token and expiration in Auth.js protected session state accessible to server-side code. Keep the client-visible session minimal. Call the Engagement resolver from the server as part of sign-in completion before showing the signed-in state. Render the protected view with a server-side Property call for verification in [2.3](phase2.3.md).
- [ ] Require a verified session before buyer search or listing access. Validate return destinations against the app's own allowed routes. For buyers, resume the search page or the same linked listing. For sellers, return to the protected workspace. Use a safe fallback for missing or invalid destinations. Use fixture destinations to verify the routing contract ahead of Phases 4 and 5.
- [ ] Handle signed-out, expired session, permission denied, and temporarily unavailable states. On expiration, start a fresh authorization flow when the user signs in again. Sign-out clears the application session and redirects through Cognito managed logout to the registered app URL. Keep protected responses out of shared caches.
- [ ] Add a local sign-in runbook section with example configuration keys, callback and sign-out URLs, and clean restart instructions. Use the existing Cognito pool with a dedicated confidential app client during [2.4](phase2.4.md). [Cognito managed logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html)

## Acceptance check

Start Next.js, a local test OIDC provider, and fixture implementations of the service contracts. Run the browser checks once against these fixtures and again against the real backend stack in [2.4](phase2.4.md).

1. Visit the public page while signed out. Open the protected page and complete sign-in. Verify the browser returns to the intended view and a refresh preserves access.
2. Sign out and revisit the protected page. Verify it prompts for sign-in. Exercise expiry and a canceled sign-in and confirm each has a recovery path.
3. Open a test buyer search route and a test listing deep link while signed out. Verify each prompts for sign-in before returning any listing data. Complete sign-in and verify the browser resumes the intended destination. Exercise an invalid return destination and confirm navigation stays within the app. Check that the client-visible session and browser-facing API responses omit access tokens and service credentials.
4. Verify a disabled account shows a forbidden state and an unavailable backend shows a recoverable service failure.

## Evidence

Record the chosen Auth.js session storage and provider configuration, frontend paths, and test results. Document the guard and return-destination rules for Phases 4, 5, and 11.
