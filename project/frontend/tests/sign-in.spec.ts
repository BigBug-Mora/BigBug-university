import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { accountId, appOrigin, clientSecret, fixtureOrigin, propertyToken, serviceToken } from "./fixture-settings.mjs";

async function setMode(request: APIRequestContext, mode: string) {
  const url = new URL("/fixture/mode", fixtureOrigin);
  url.searchParams.set("value", mode);
  expect((await request.post(url.toString())).ok()).toBeTruthy();
}

async function begin(page: Page) {
  await page.getByRole("button", { name: "Sign in with Cognito" }).click();
  await expect(page.getByRole("heading", { name: "Test identity provider" })).toBeVisible();
}

async function approve(page: Page) {
  await begin(page);
  await page.getByRole("link", { name: "Approve sign-in" }).click();
}

test.beforeEach(async ({ request }) => {
  await setMode(request, "active");
});

test("buyer enters from home, refreshes, and signs out through managed logout", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Continue as buyer" }).click();
  await expect(page.getByRole("heading", { name: "Sign in", exact: true })).toBeVisible();
  await expect(page.getByText(accountId)).toHaveCount(0);
  await approve(page);
  await expect(page).toHaveURL("/buyer/search");
  await expect(page.getByRole("heading", { name: "Buyer search" })).toBeVisible();
  await expect(page.getByText(accountId)).toBeVisible();
  const protectedResponse = await page.reload();
  expect(protectedResponse?.headers()["cache-control"]).toContain("no-store");
  await expect(page.getByText(accountId)).toBeVisible();

  const response = await page.request.get("/api/auth/session");
  expect(response.headers()["cache-control"]).toContain("no-store");
  expect(await response.json()).toEqual({ expires: expect.any(String) });
  const markup = await page.content();
  expect(markup).not.toContain(serviceToken);
  expect(markup).not.toContain(propertyToken);
  expect(markup).not.toContain(clientSecret);
  expect(markup).not.toContain("accessToken");

  const logoutRequest = page.waitForRequest((request) => request.url().startsWith(`${fixtureOrigin}/logout?`));
  await page.getByRole("button", { name: "Sign out" }).click();
  expect(new URL((await logoutRequest).url()).searchParams.get("logout_uri")).toBe(`${appOrigin}/`);
  await expect(page).toHaveURL("/");
  expect(await (await page.request.get("/api/auth/session")).json()).toBeNull();
  await page.goto("/buyer/search");
  await expect(page.getByRole("heading", { name: "Sign in", exact: true })).toBeVisible();
});

test("the seller entry opens the protected workspace", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Continue as seller" }).click();
  await approve(page);
  await expect(page).toHaveURL("/seller/workspace");
  await expect(page.getByRole("heading", { name: "Seller workspace" })).toBeVisible();
});

test("buyer deep link prompts for sign-in and resumes the same listing", async ({ page }) => {
  await page.goto("/buyer/listings/courtyard-house");
  await expect(page.getByRole("heading", { name: "Sign in", exact: true })).toBeVisible();
  await expect(page.getByText("Listing courtyard-house")).toHaveCount(0);
  await approve(page);
  await expect(page).toHaveURL("/buyer/listings/courtyard-house");
  await expect(page.getByRole("heading", { name: "Listing courtyard-house" })).toBeVisible();
});

test("an invalid return destination falls back to buyer search", async ({ page }) => {
  await page.goto("/sign-in?returnTo=%2F%2Foutside.invalid%2Fbuyer%2Fsearch");
  await approve(page);
  await expect(page).toHaveURL("/buyer/search");
});

test("canceled sign-in can be retried at the original destination", async ({ page }) => {
  await page.goto("/buyer/listings/courtyard-house");
  await begin(page);
  await page.getByRole("link", { name: "Cancel sign-in" }).click();
  await expect(page.getByRole("heading", { name: "Sign-in could not be completed" })).toBeVisible();
  await approve(page);
  await expect(page).toHaveURL("/buyer/listings/courtyard-house");
});

test("Auth.js rejects a callback whose state does not match", async ({ page, request }) => {
  await setMode(request, "invalid-state");
  await page.goto("/buyer/search");
  await approve(page);
  await expect(page.getByRole("heading", { name: "Sign-in could not be completed" })).toBeVisible();
  expect(await (await page.request.get("/api/auth/session")).json()).toBeNull();
});

test("an expired access token requires a fresh authorization flow", async ({ page, request }) => {
  await setMode(request, "short-session");
  await page.goto("/buyer/search");
  await approve(page);
  await expect(page.getByRole("heading", { name: "Buyer search" })).toBeVisible();
  const { expires } = await (await page.request.get("/api/auth/session")).json();
  await expect.poll(() => Date.now() >= Date.parse(expires), { timeout: 7000 }).toBe(true);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Session expired" })).toBeVisible();
  await setMode(request, "active");
  await approve(page);
  await expect(page).toHaveURL("/buyer/search");
});

for (const [mode, title] of [
  ["forbidden", "Access denied"],
  ["outage", "Service temporarily unavailable"],
  ["malformed-account", "Service temporarily unavailable"],
] as const) {
  test(`sign-in is blocked when Engagement returns ${mode}`, async ({ page, request }) => {
    await setMode(request, mode);
    await page.goto("/seller/workspace");
    await approve(page);
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
    expect(await (await page.request.get("/api/auth/session")).json()).toBeNull();
    await setMode(request, "active");
    await approve(page);
    await expect(page).toHaveURL("/seller/workspace");
  });
}

test("access is rechecked and recovers after a backend outage", async ({ page, request }) => {
  await page.goto("/buyer/search");
  await approve(page);
  await expect(page.getByText(accountId)).toBeVisible();

  await setMode(request, "property-outage");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Service temporarily unavailable" })).toBeVisible();
  await expect(page.getByText(accountId)).toHaveCount(0);
  await setMode(request, "active");
  await page.reload();
  await expect(page.getByText(accountId)).toBeVisible();

  await setMode(request, "forbidden");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Access denied" })).toBeVisible();
  await expect(page.getByText(accountId)).toHaveCount(0);
});
