# Phase 2.4 · CI and shared Cognito acceptance

Run the browser and API acceptance checks against a clean local stack. Then repeat the sign-in path with the existing Cognito test users and shared RDS using the application's own app client.

[Phase 2](phase2.md) · [CI design](../../mvp/ci/cd/ci.md#github-actions-workflow) · [Phase 1.4 shared AWS evidence](../phase-01/phase1.4.md) · [Shared AWS runbook](../../../infra/runbooks/shared-aws-development.md) · [Cognito app client settings](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)

## Progress

- [ ] Extend `.github/workflows/ci.yml` to install the pinned frontend and backend dependencies and run the 2.1–2.3 checks. Reuse disposable PostgreSQL and the existing migrations, fixture assertions, and Property health smoke. Run frontend lint, type checking, and the committed frontend test commands.
- [ ] Build Frontend, Property, and Engagement in Compose. Run the browser acceptance flow against those images with a local test OIDC provider and JWKS. Use an issuer URL that resolves consistently from the browser and app containers. Have the test provider issue access tokens with the same claim shape the production verifier expects. Use the same Auth.js, verifier, resolver, and database paths as the live flow. Configure test issuers and credentials only in the test setup. Clean up the application and disposable database stacks on failure and success, and keep diagnostic output free of secrets.
- [ ] Document exact local commands, supported configuration and ports, and expected results in the README or linked runbook. Keep the original Phase 1 startup and test instructions usable.
- [ ] Provision the dedicated confidential Auth.js app client in the shared Cognito pool. Enable authorization-code flow, register the exact development callback and sign-out URLs, and verify the requested scopes. Reuse the existing buyer and seller identities and keep the Phase 1 PKCE client available for its smoke script.
- [ ] Review shared database access. Confirm the migration head, provision the dedicated Engagement runtime login and grants, and check that the running Engagement app can reach the existing SSM tunnel using the RDS CA bundle and full hostname verification. Document the tunnel address from the app's runtime environment. Apply any required reviewed migrations explicitly before starting the shared stack.
- [ ] Record successful CI and live Cognito evidence below. Tick the phase plan and roadmap only after both checks pass.

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
| Local disposable stack | Date, exact commands, Git revision, and results for startup, browser flow, account stability, and denial cases. |
| Pull request | Passing Actions run link and job names. |
| Shared smoke | Date, tested Git revision, verified migration head, configured session lifetime, and anonymized results for buyer, seller, repeat sign-in, sign-out, and denial. |
| Handoff | Runtime role and configuration names, verified startup commands, and any remaining owner or dependency. |
