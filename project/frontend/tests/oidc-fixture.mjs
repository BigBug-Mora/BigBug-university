import { createHash, generateKeyPairSync, randomUUID, sign } from "node:crypto";
import { createServer } from "node:http";
import {
  accountId, callbackUrl, clientId, clientSecret, fixtureOrigin, appOrigin, serviceToken,
} from "./fixture-settings.mjs";

const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
const kid = "estateflow-local";
const requests = new Map();
const codes = new Map();
const tokens = new Map();
let mode = "active";

function issueToken(claims) {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString("base64url");
  const data = `${encode({ alg: "RS256", kid, typ: "JWT" })}.${encode(claims)}`;
  const signature = sign("RSA-SHA256", Buffer.from(data), privateKey).toString("base64url");
  return `${data}.${signature}`;
}

function json(response, status, value) {
  response.writeHead(status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
  response.end(JSON.stringify(value));
}

function redirect(response, url) {
  response.writeHead(302, { Location: url.toString(), "Cache-Control": "no-store" });
  response.end();
}

function authorize(query, response) {
  const auth = Object.fromEntries(query);
  if (
    auth.client_id !== clientId || auth.redirect_uri !== callbackUrl || auth.scope !== "openid" ||
    auth.response_type !== "code" || auth.prompt !== "login" || auth.code_challenge_method !== "S256" ||
    !auth.state || !auth.code_challenge || !auth.nonce
  ) {
    return json(response, 400, { error: "invalid_request" });
  }
  const id = randomUUID();
  requests.set(id, auth);
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(`<!doctype html><title>EstateFlow test identity</title>
    <h1>Test identity provider</h1>
    <a href="/finish?id=${id}&amp;approve=1">Approve sign-in</a>
    <a href="/finish?id=${id}">Cancel sign-in</a>`);
}

function finish(query, response) {
  const id = query.get("id");
  const auth = requests.get(id);
  if (!auth) return json(response, 400, { error: "invalid_request" });
  requests.delete(id);
  const callback = new URL(callbackUrl);
  callback.searchParams.set("state", mode === "invalid-state" ? "invalid-state" : auth.state);
  if (query.has("approve")) {
    const code = randomUUID();
    codes.set(code, auth);
    callback.searchParams.set("code", code);
  } else {
    callback.searchParams.set("error", "access_denied");
  }
  redirect(response, callback);
}

async function exchange(request, response) {
  let body = "";
  for await (const chunk of request) body += chunk;
  const parameters = new URLSearchParams(body);
  const code = parameters.get("code");
  const auth = codes.get(code);
  codes.delete(code);
  const verifier = parameters.get("code_verifier") ?? "";
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  const basic = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
  if (
    !auth || request.headers.authorization !== `Basic ${basic}` ||
    parameters.get("grant_type") !== "authorization_code" ||
    parameters.get("redirect_uri") !== callbackUrl || auth.code_challenge !== challenge
  ) {
    return json(response, 400, { error: "invalid_grant" });
  }
  const now = Math.floor(Date.now() / 1000);
  const expiresIn = mode === "short-session" ? 5 : 300;
  const common = { iss: fixtureOrigin, sub: "fixture-buyer", iat: now, exp: now + expiresIn };
  const access = issueToken({ ...common, client_id: clientId, token_use: "access", jti: randomUUID() });
  tokens.set(access, common.exp);
  return json(response, 200, {
    access_token: access,
    expires_in: expiresIn,
    token_type: "Bearer",
    id_token: issueToken({ ...common, aud: clientId, nonce: auth.nonce, token_use: "id" }),
  });
}

function resolve(request, response) {
  const access = request.headers.authorization?.slice("Bearer ".length);
  if (request.headers["x-estateflow-service-token"] !== serviceToken ||
      !request.headers.authorization?.startsWith("Bearer ") || !(tokens.get(access) > Date.now() / 1000)) {
    return json(response, 401, { detail: "Unauthorized" });
  }
  if (mode === "forbidden") return json(response, 403, { detail: "Forbidden" });
  if (mode === "outage") return json(response, 503, { detail: "Service unavailable" });
  return json(response, 200, { account_id: mode === "malformed-account" ? "invalid" : accountId });
}

const server = createServer((request, response) => {
  const { pathname, searchParams } = new URL(request.url, fixtureOrigin);
  switch (`${request.method} ${pathname}`) {
    case "GET /":
      return json(response, 200, { status: "ok" });
    case "GET /.well-known/openid-configuration":
      return json(response, 200, {
        issuer: fixtureOrigin,
        authorization_endpoint: `${fixtureOrigin}/authorize`,
        token_endpoint: `${fixtureOrigin}/token`,
        userinfo_endpoint: `${fixtureOrigin}/userinfo`,
        jwks_uri: `${fixtureOrigin}/.well-known/jwks.json`,
        response_types_supported: ["code"],
        subject_types_supported: ["public"],
        id_token_signing_alg_values_supported: ["RS256"],
        code_challenge_methods_supported: ["S256"],
        token_endpoint_auth_methods_supported: ["client_secret_basic"],
      });
    case "GET /.well-known/jwks.json":
      return json(response, 200, { keys: [{ ...publicKey.export({ format: "jwk" }), kid, alg: "RS256", use: "sig" }] });
    case "GET /authorize":
      return authorize(searchParams, response);
    case "GET /finish":
      return finish(searchParams, response);
    case "POST /token":
      return exchange(request, response).catch(() => json(response, 400, { error: "invalid_request" }));
    case "GET /userinfo":
      if (tokens.get(request.headers.authorization?.slice("Bearer ".length)) > Date.now() / 1000) {
        return json(response, 200, { sub: "fixture-buyer" });
      }
      return json(response, 401, { error: "invalid_token" });
    case "POST /internal/accounts/resolve":
      return resolve(request, response);
    case "POST /fixture/mode":
      mode = searchParams.get("value");
      return json(response, 200, { status: "ok" });
    case "GET /logout":
      if (searchParams.get("client_id") === clientId && searchParams.get("logout_uri") === `${appOrigin}/`) {
        return redirect(response, `${appOrigin}/`);
      }
      return json(response, 400, { error: "invalid_request" });
    default:
      return json(response, 404, { error: "not_found" });
  }
});

server.listen(Number(new URL(fixtureOrigin).port), "127.0.0.1");
