# Phase 2 · Identity and account access

Establish a browser sign-in flow and a backend authentication boundary that later listing and conversation work can reuse. A returning Cognito user resolves to the same EstateFlow account across sessions and services. Each protected API derives its actor from verified credentials.

[Roadmap](../roadmap.md) · [Repository layout](../repository-layout.md) · [Phase 1 handoff](../phase-01/phase1.md#discoveries-and-handoff)

## Progress and order

- [x] [2.1 · Verified identity and account mapping](phase2.1.md). Use the Phase 1 schema and disposable PostgreSQL 17. Verify signed test identities and resolve accounts through Engagement.
- [x] [2.2 · Frontend sign-in and session](phase2.2.md). Use the 2.1 API contract. A local test identity provider and fixture responses allow independent frontend work.
- [ ] [2.3 · Protected service calls](phase2.3.md). Use the 2.1 verifier and resolver. Exercise Property directly with signed test identities before integrating 2.2.
- [ ] [2.4 · CI and shared Cognito acceptance](phase2.4.md). Integrate 2.1–2.3. Run the full local stack in CI and verify the same user path with live Cognito and shared RDS.

## Scope and ownership

| Owner | Deliverable |
| --- | --- |
| Frontend | Next.js and Auth.js handle sign-in, sign-out, session expiry, and backend calls on the signed-in user's behalf. |
| Engagement | Owns `account.accounts` and `account.profiles`. Maps the verified Cognito issuer and subject to an application UUID and checks current account status. |
| Property | Verifies actor context on its first protected endpoint. It resolves the account through Engagement. Phase 3 will add listing ownership checks here. |
| Shared Python code | Verifies Cognito access tokens and authenticates internal callers. Service handlers and account writes stay with their owners. |
| CI and infrastructure | Add deterministic identity checks to the existing workflow and document the separate shared Cognito app client, database role, and live smoke steps. |

Use the existing PostgreSQL 17 schema and the Phase 1 Cognito test users. Preserve the Property health check and local entry point. Future phases own the listing editor, public listings and search, persisted chat, and private disclosures. Public registration, profile editing, and hosted deployment are outside this phase.

[Container rules](../../mvp/containers/containers.md#cross-container-rules) · [Database authorization](../../mvp/database/contracts.md#ownership-and-authorization) · [Frontend permissions](../../mvp/containers/frontend/frontend.md#permissions-and-failures) · [CI design](../../mvp/ci/cd/ci.md#github-actions-workflow)

## Phase acceptance

1. From a clean checkout, follow the documented local commands to migrate disposable PostgreSQL, load the Phase 1 fixtures, and start the stack with the deterministic identity provider. Run the identity suites and browser flow in [2.4](phase2.4.md).
2. Sign in as the first test identity, reload the protected page, sign out, and sign in again. The account UUID returned by Engagement and Property must match across sessions. Sign in as a second identity and confirm a different UUID.
3. Call the protected Property endpoint with missing or invalid credentials and confirm denial. With valid user and caller credentials, confirm a successful response. Confirm a disabled account is denied and resolver failure never grants access. Property's public health check must still pass.
4. Verify the pull-request checks pass and record the run link. Repeat the browser sign-in, account stability, and denial smoke checks using the shared Cognito app client and RDS. Record the commands, revision, date, and outcomes in [2.4](phase2.4.md) before ticking Phase 2 in the roadmap.

## Decisions and open questions

- **Buyer sign-in entry, confirmed.** Buyers sign in before searching or opening a listing, including when following a direct listing link. After sign-in, resume the requested search page or listing. Sellers sign in on entry to the seller workspace. Phase 2 establishes the route and API guards. Phases 4, 5, and 11 apply them to the published listing page and both search paths. [Frontend permissions](../../mvp/containers/frontend/frontend.md#permissions-and-failures) · [Buyer Agent search](../../mvp/containers/agent-api/buyer-agent.md#search-mode)
- **Account identity.** Use the existing unique issuer and subject pair. Buyer and seller describe the account's relationship to a resource. Both Phase 1 test users use the same sign-in flow.
- **Credential handoff.** Forward the Cognito access token from server to server. Authenticate the caller separately using credentials scoped to each caller and receiver. The receiving service verifies the user token and enforces its own permissions. See [2.1](phase2.1.md#internal-api-contract) and [2.3](phase2.3.md#protected-api-contract).
- **Session lifetime.** Use reauthentication when the access token expires for this phase. Implement sign-out for both the app session and Cognito managed login. Record the configured lifetimes and the observed behavior in [2.4](phase2.4.md).
- **Phase 1 handoff.** The owner verified the shared AWS dependencies and waived the second-machine check for Phase 1. Phase 2 deliberately tests the application flow through its dedicated Auth.js client and an Engagement runtime login.

## Downstream handoff

Phase 3 uses the Property actor dependency to enforce draft ownership. Phases 4 and 5 guard published listing reads and structured search. Phase 11 applies the actor contract to Buyer Agent search. Phase 12 uses the same verified account for conversation membership. Phase 14 uses that account for disclosure grants. Phase 17 configures the final hosted frontend origin and its Cognito callback and sign-out URLs.
