export const appOrigin = `http://127.0.0.1:${process.env.ESTATEFLOW_TEST_FRONTEND_PORT ?? 47120}`;
export const fixtureOrigin = `http://127.0.0.1:${process.env.ESTATEFLOW_TEST_OIDC_PORT ?? 47121}`;
export const callbackUrl = `${appOrigin}/api/auth/callback/cognito`;
export const clientId = "estateflow-fixture-client";
export const clientSecret = "estateflow-fixture-client-secret";
export const serviceToken = "estateflow-fixture-frontend-token";
export const accountId = "c0c0160c-9b20-4dc2-8d42-2ea6de091c78";

export const appEnvironment = {
  AUTH_URL: appOrigin,
  AUTH_SECRET: "estateflow-local-playwright-session-secret-never-for-hosting",
  ESTATEFLOW_COGNITO_ISSUER: fixtureOrigin,
  ESTATEFLOW_COGNITO_CLIENT_ID: clientId,
  ESTATEFLOW_COGNITO_CLIENT_SECRET: clientSecret,
  ESTATEFLOW_COGNITO_LOGIN_ORIGIN: fixtureOrigin,
  ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER: "1",
  ESTATEFLOW_ENGAGEMENT_BASE_URL: fixtureOrigin,
  ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN: serviceToken,
  NEXT_TELEMETRY_DISABLED: "1",
};
