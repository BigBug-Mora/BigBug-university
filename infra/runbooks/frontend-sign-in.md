# Frontend sign-in

Use Node.js 24 and run the commands below from `project/frontend`. The browser tests use a local identity provider and fixtures for the Engagement and Property APIs. Phase 2.4 exercises the live stack with the dedicated confidential Cognito app client.

## Verify with local fixtures

```sh
npm ci
npx playwright install chromium
npm run lint
npm run build
npm run typecheck
npm run test:e2e
```

Playwright starts the production build on `http://127.0.0.1:47120` and the test OIDC provider and API fixture on `http://127.0.0.1:47121`. It supplies fictional credentials and stops both processes when the run ends. If a port is reserved, use `ESTATEFLOW_TEST_FRONTEND_PORT` or `ESTATEFLOW_TEST_OIDC_PORT` to select an available loopback port.

## Configure the frontend for Cognito

Copy `.env.example` to `.env.local` and fill in these values. Keep the file local. Generate `AUTH_SECRET` with `node -e "console.log(require('node:crypto').randomBytes(32).toString('base64'))"` and save the generated value.

| Setting | Value |
| --- | --- |
| `AUTH_URL` | Browser-facing app origin, for example `http://localhost:3000`. Use that same origin in the browser. |
| `AUTH_SECRET` | Secret used to encrypt Auth.js session state. |
| `ESTATEFLOW_COGNITO_ISSUER` | User-pool issuer under `https://cognito-idp.<region>.amazonaws.com/<pool-id>`. |
| `ESTATEFLOW_COGNITO_CLIENT_ID` | ID of the dedicated confidential app client with authorization-code flow and `openid`. |
| `ESTATEFLOW_COGNITO_CLIENT_SECRET` | Secret of that app client. |
| `ESTATEFLOW_COGNITO_LOGIN_ORIGIN` | HTTPS origin of the Cognito managed login domain. The app uses its `/logout` endpoint. |
| `ESTATEFLOW_ENGAGEMENT_BASE_URL` | Origin of the running Engagement service as reached by the Next.js server. |
| `ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN` | Credential shared by Frontend and Engagement for the account resolver. |
| `ESTATEFLOW_PROPERTY_BASE_URL` | Origin of the running Property service as reached by the Next.js server. |
| `ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN` | Separate credential shared by Frontend and Property for the protected account view. |

Register the exact callback `http://localhost:3000/api/auth/callback/cognito` and sign-out URL `http://localhost:3000/` for the example origin. If the origin changes, register both URLs for that origin. The fixture-only `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER=1` permits the local identity provider and logout endpoint to use HTTP.

Run `npm ci` and `npm run dev`. Visit the configured origin. To restart with changed settings, stop Next.js with Ctrl+C and run `npm run dev` again. After changing origin, client, or session secret, use a new private browser window to start with fresh cookies.

To build the standalone frontend container, run `docker build -t estateflow-frontend .` from `project/frontend`. Pass runtime settings using an environment file or the service's secret configuration. The browser origin must match the exposed host port, and the internal Engagement and Property origins must be reachable from the container.

## Run the identity stack with Compose

From the repository root, copy `project/.env.identity.example` to `project/.env.identity`. Fill in the Cognito and Auth.js settings above and set `ESTATEFLOW_ENGAGEMENT_DATABASE_URL` to a connection string for the [scoped Engagement login](shared-aws-development.md#engagement-runtime-login) reachable from the Engagement container. Run the random-secret command above three times to generate separate values for Frontend → Engagement, Frontend → Property, and Property → Engagement. Compose supplies the same value to both ends of each connection.

```sh
docker compose --env-file project/.env.identity -f project/compose.yaml --profile identity up --build --detach --wait
docker compose --env-file project/.env.identity -f project/compose.yaml --profile identity down
```

Open `http://localhost:3000` for sign-in. The services use Compose DNS on the project's bridge network. Engagement has no published port. The Property port is bound to loopback for the existing health smoke check. Running Compose without the identity profile and without identity settings starts the Property health service on its own. The protected route returns 503 in this mode.

Phase 17 hosting requires private backend endpoints, encrypted transport with certificate verification for internal calls, and runtime secret distribution scoped to each service and connection. The HTTP service origins in the example are for local Compose.
