# Frontend sign-in

Use Node.js 24 and run the commands below from `project/frontend`. Phase 2.2 uses a local identity provider and a fixture for the Engagement API. Phase 2.4 exercises the live stack with the dedicated confidential Cognito app client.

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

Register the exact callback `http://localhost:3000/api/auth/callback/cognito` and sign-out URL `http://localhost:3000/` for the example origin. If the origin changes, register both URLs for that origin. The fixture-only `ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER=1` permits the local identity provider and logout endpoint to use HTTP.

Run `npm ci` and `npm run dev`. Visit the configured origin. To restart with changed settings, stop Next.js with Ctrl+C and run `npm run dev` again. After changing origin, client, or session secret, use a new private browser window to start with fresh cookies.

To build the standalone frontend container, run `docker build -t estateflow-frontend .` from `project/frontend`. Pass runtime settings using an environment file or the service's secret configuration. The browser origin must match the exposed host port, and the internal Engagement origin must be reachable from the container.
