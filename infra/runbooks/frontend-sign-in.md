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

## Verify the complete identity stack

Use Python 3.14, Node.js 24, and Docker Compose with Linux containers. From a clean checkout, activate a Python virtual environment and run these commands at the repository root. On a Linux host without the Chromium system dependencies, use `--with-deps` when installing Chromium.

```sh
python -m pip install -r project/requirements.txt -r project/services/property/tests/requirements.txt -r project/services/engagement/tests/requirements.txt
python -m pip check
cd project/frontend
npm ci
npx playwright install chromium
npm run lint
npm run build
npm run typecheck
npm run test:e2e
cd ../..
python project/tests/integration/identity_acceptance.py
```

The final command recreates the dedicated `estateflow-identity-test` Compose project and removes its containers and network on exit. Reserve loopback ports 3000 for Frontend, 8000 for Property, 55432 for disposable PostgreSQL, and 47121 for the identity fixture. Compose resolves `identity-fixture` on its bridge network and Playwright maps the same hostname to loopback in Chromium. The runner supplies fictional credentials and selects the full-stack browser test. Each suite must pass, Alembic must reach head on a repeat upgrade, and the full-stack test must verify sign-in, sign-out, UUID stability, distinct accounts, Property health, credential denial, disabled accounts, and resolver failure.

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

From the repository root, copy `project/.env.identity.example` to `project/.env.identity`. Fill in the Cognito and Auth.js settings above and set `ESTATEFLOW_ENGAGEMENT_DATABASE_URL` and `ESTATEFLOW_PROPERTY_DATABASE_URL` to connection strings for the [scoped Engagement login](shared-aws-development.md#engagement-runtime-login) and [scoped Property login](shared-aws-development.md#property-runtime-login) reachable from the containers. Also configure `ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF` and `ESTATEFLOW_PRIVATE_DETAIL_KEYS` (Fernet key map for encrypted private details). Run the random-secret command above three times to generate separate values for Frontend → Engagement, Frontend → Property, and Property → Engagement. Compose supplies the same value to both ends of each connection.

```sh
docker compose --env-file project/.env.identity -f project/compose.yaml --profile identity up --build --detach --wait
docker compose --env-file project/.env.identity -f project/compose.yaml --profile identity down
```

Open `http://localhost:3000` for sign-in. The services use Compose DNS on the project's bridge network. Engagement has no published port. The Property port is bound to loopback for the existing health smoke check. Running Compose without the identity profile and without identity settings starts the Property health service on its own. The protected route returns 503 in this mode.

Phase 17 hosting requires private backend endpoints, encrypted transport with certificate verification for internal calls, and runtime secret distribution scoped to each service and connection. The HTTP service origins in the example are for local Compose.

## Verify shared Cognito and RDS

Use the dedicated confidential `estateflow-dev-authjs` client in the shared pool. Configure Cognito as its identity provider and enable the authorization-code grant with scope `openid`. Set the callback to `http://localhost:3000/api/auth/callback/cognito` and sign-out URL to `http://localhost:3000/`. On a Managed Login v2 domain, an app client created through the AWS CLI also requires Managed Login branding (`aws cognito-idp create-managed-login-branding --use-cognito-provided-values`), or `/login` will report that login pages are unavailable. The development client uses 60-minute access and ID tokens and a one-day refresh token. The application session has an eight-hour maximum and requests reauthentication when the Cognito access token expires.

Open the [SSM tunnel and verify the database head](shared-aws-development.md#3-open-the-tunnel-bootstrap-roles-and-apply-migrations). Provision the [Engagement runtime login](shared-aws-development.md#engagement-runtime-login) and [Property runtime login](shared-aws-development.md#property-runtime-login), and set up `project/.env.identity` as above. On Docker Desktop, resolve the host-side address from a Linux container while the tunnel is running. On native WSL2 Docker Engine, see the [WSL2 note](shared-aws-development.md#native-wsl2-docker-engine-note).

```powershell
docker run --rm postgres:17-bookworm getent ahostsv4 host.docker.internal
$env:ESTATEFLOW_RDS_CA_FILE = (Resolve-Path '<path to the AWS RDS CA bundle>').Path
```

Set `ESTATEFLOW_ENGAGEMENT_DATABASE_URL` in the local identity environment file to a libpq connection string with `host=<RDS endpoint> hostaddr=<numeric Docker host address> port=15432 dbname=estateflow_app user=estateflow_engagement password=<runtime password> sslmode=verify-full sslrootcert=/rds-ca.pem`. Use the RDS Compose override to mount the certificate into Engagement. On other Docker setups, supply the address of a tunnel listener reachable from the Engagement container.

```powershell
$stack = @('-p', 'estateflow-identity-live', '--env-file', 'project/.env.identity', '-f', 'project/compose.yaml', '-f', 'project/compose.identity-rds.yaml', '--profile', 'identity')
docker compose @stack up --build --detach --wait
docker compose @stack exec -T engagement-service python -c "import os, psycopg; db = psycopg.connect(os.environ['ESTATEFLOW_ENGAGEMENT_DATABASE_URL']); print(db.execute('SELECT current_user, ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()').fetchone()); db.close()"
```

Expect `('estateflow_engagement', True)`. In a fresh browser context, open the buyer listing fixture and sign in through Cognito. Refresh and compare the account UUID. Check that `/api/auth/session` contains only the expiry. Sign out, confirm the protected page prompts for sign-in, and sign in again to check the same UUID. Use a separate context for the seller and check for a distinct UUID. Confirm denial and health through the loopback Property port.

```powershell
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/internal/identity/me
curl.exe --fail http://127.0.0.1:8000/health
docker compose @stack down
```

Expect `401` and `{"status":"ok"}`. Stop the SSM session after the smoke test and record the tested revision and anonymized results in the [Phase 2.4 plan](../../Documentation/implementation/phase-02/phase2.4.md).
