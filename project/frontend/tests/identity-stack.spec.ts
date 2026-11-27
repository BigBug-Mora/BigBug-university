import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";
import { fixtureOrigin, propertyToken } from "./fixture-settings.mjs";

const listing = "/buyer/listings/courtyard-house";
const property = "http://127.0.0.1:8000";
const uuid = /^[\da-f]{8}(?:-[\da-f]{4}){3}-[\da-f]{12}$/;

function compose(...args: string[]) {
  return execFileSync("docker", [
    "compose", "-p", "estateflow-identity-test", "-f", "project/compose.yaml",
    "-f", "project/compose.test.yaml", "-f", "project/compose.identity-test.yaml",
    "--profile", "identity", ...args,
  ], {
    cwd: fileURLToPath(new URL("../../../", import.meta.url)),
    encoding: "utf8",
    timeout: 15_000,
  }).trim();
}

function database(sql: string) {
  return compose("exec", "-T", "db", "psql", "-XAtq", "-U", "estateflow_migrator",
    "-d", "estateflow_test", "-v", "ON_ERROR_STOP=1", "-c", sql);
}

async function signIn(page: Page, destination: string, heading: string, seller = false) {
  await page.goto(destination);
  await expect(page.getByRole("heading", { name: "Sign in", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Sign in with Cognito" }).click();
  await expect(page.getByRole("heading", { name: "Test identity provider" })).toBeVisible();
  await page.getByRole("link", { name: seller ? "Approve as seller" : "Approve sign-in" }).click();
  await expect(page).toHaveURL(destination);
  await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  const account = await page.getByText(uuid).innerText();
  expect(account).toMatch(uuid);
  return account;
}

async function signOut(page: Page) {
  const logout = page.waitForRequest((request) => request.url().startsWith(`${fixtureOrigin}/logout?`));
  await page.getByRole("button", { name: "Sign out" }).click();
  await logout;
  await expect(page).toHaveURL("/");
  expect(await (await page.request.get("/api/auth/session")).json()).toBeNull();
}

test("the Compose images resolve browser identities and enforce current account access", async ({ page, request }) => {
  test.setTimeout(90_000);
  const health = await request.get(`${property}/health`);
  expect(health.status()).toBe(200);
  expect(await health.json()).toEqual({ status: "ok" });
  const credentials: Record<string, string>[] = [
    {}, { "X-EstateFlow-Service-Token": propertyToken, Authorization: "Bearer invalid" },
  ];
  for (const headers of credentials) {
    const denied = await request.get(`${property}/internal/identity/me`, { headers });
    expect(denied.status()).toBe(401);
    expect(await denied.json()).toEqual({ detail: "Unauthorized" });
  }

  const buyer = await signIn(page, listing, "Listing courtyard-house");
  const refresh = await page.reload();
  expect(refresh?.headers()["cache-control"]).toContain("no-store");
  await expect(page.getByText(buyer)).toBeVisible();
  expect(await (await page.request.get("/api/auth/session")).json()).toEqual({ expires: expect.any(String) });
  await signOut(page);
  expect(await signIn(page, listing, "Listing courtyard-house")).toBe(buyer);
  await signOut(page);
  const seller = await signIn(page, "/seller/workspace", "Seller workspace", true);
  expect(seller).not.toBe(buyer);
  expect(database("SELECT id FROM account.accounts WHERE cognito_subject = 'fixture-buyer'")).toBe(buyer);
  expect(database("SELECT id FROM account.accounts WHERE cognito_subject = 'fixture-seller'")).toBe(seller);

  database("UPDATE account.accounts SET status = 'disabled' WHERE cognito_subject = 'fixture-seller'");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Access denied" })).toBeVisible();
  await expect(page.getByText(seller)).toHaveCount(0);

  database("UPDATE account.accounts SET status = 'active' WHERE cognito_subject = 'fixture-seller'");
  await page.reload();
  await expect(page.getByText(seller)).toBeVisible();
  compose("stop", "--timeout", "5", "engagement-service");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Service temporarily unavailable" })).toBeVisible();
  await expect(page.getByText(seller)).toHaveCount(0);
});
