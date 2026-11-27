import "server-only";

function required(name: string): string {
  const value = process.env[name];
  if (!value?.trim()) throw new Error(`Set ${name} in the frontend runtime.`);
  return value;
}

function endpoint(name: string): URL {
  const url = new URL(required(name));
  if (
    !["http:", "https:"].includes(url.protocol) ||
    url.username || url.password || url.search || url.hash
  ) {
    throw new Error(`Set a valid HTTP or HTTPS URL for ${name}.`);
  }
  return url;
}

export function appOrigin(): string {
  return origin("AUTH_URL");
}

function origin(name: string): string {
  const url = endpoint(name);
  if (url.pathname !== "/") throw new Error(`Set an origin without a path for ${name}.`);
  return url.origin;
}

export function sessionSettings() {
  const secure = appOrigin().startsWith("https:");
  const prefix = secure ? "__Secure-" : "";
  return {
    secure,
    secret: required("AUTH_SECRET"),
    sessionCookie: `${prefix}authjs.session-token`,
    callbackCookie: `${prefix}authjs.callback-url`,
  };
}

export function cognitoSettings() {
  const issuer = endpoint("ESTATEFLOW_COGNITO_ISSUER");
  const loginOrigin = origin("ESTATEFLOW_COGNITO_LOGIN_ORIGIN");
  const allowTestHttp = process.env.ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER === "1";
  if (!allowTestHttp && (issuer.protocol !== "https:" || !loginOrigin.startsWith("https:"))) {
    throw new Error("Use HTTPS for Cognito issuer and managed login.");
  }
  return {
    issuer: issuer.href.replace(/\/$/, ""),
    loginOrigin,
    clientId: required("ESTATEFLOW_COGNITO_CLIENT_ID"),
    clientSecret: required("ESTATEFLOW_COGNITO_CLIENT_SECRET"),
  };
}

export function engagementSettings() {
  return {
    origin: origin("ESTATEFLOW_ENGAGEMENT_BASE_URL"),
    serviceToken: required("ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN"),
  };
}
