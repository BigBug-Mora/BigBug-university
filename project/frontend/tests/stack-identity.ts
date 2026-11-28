import { createHash, randomUUID } from "node:crypto";
import { expect, type APIRequestContext, type Page } from "@playwright/test";
import { callbackUrl, clientId, clientSecret, propertyToken } from "./fixture-settings.mjs";

const provider = "http://127.0.0.1:47121";

export async function propertyCredentials(request: APIRequestContext, identity: "seller" | "buyer") {
  const verifier = randomUUID() + randomUUID();
  const login = await request.get(provider + "/authorize", { params: {
    client_id: clientId, redirect_uri: callbackUrl, scope: "openid", response_type: "code", prompt: "login",
    code_challenge_method: "S256", code_challenge: createHash("sha256").update(verifier).digest("base64url"),
    state: randomUUID(), nonce: randomUUID(),
  } });
  const id = /finish\?id=([a-f0-9-]+)/.exec(await login.text())?.[1];
  if (!id) throw new Error("Fixture authorization unavailable");
  const approved = await request.get(provider + "/finish", { params: { id, approve: "1", identity }, maxRedirects: 0 });
  const code = new URL(approved.headers().location).searchParams.get("code")!;
  const token = await request.post(provider + "/token", {
    headers: { Authorization: "Basic " + Buffer.from(clientId + ":" + clientSecret).toString("base64") },
    form: { code, code_verifier: verifier, grant_type: "authorization_code", redirect_uri: callbackUrl },
  });
  expect(token.ok()).toBeTruthy();
  return { Authorization: "Bearer " + (await token.json()).access_token, "X-EstateFlow-Service-Token": propertyToken };
}

export async function signInAs(page: Page, destination: string, identity: "seller" | "buyer") {
  await page.goto(destination);
  await expect(page.getByRole("heading", { name: "Sign in", exact: true })).toBeVisible();
  expect(new URL(page.url()).searchParams.get("returnTo")).toBe(destination);
  await page.getByRole("button", { name: "Sign in with Cognito" }).click();
  await page.getByRole("link", { name: identity === "seller" ? "Approve as seller" : "Approve sign-in" }).click();
  await expect(page).toHaveURL(destination);
}
