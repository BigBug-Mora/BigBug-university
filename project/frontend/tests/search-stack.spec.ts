import { expect, test } from "@playwright/test";
import { appOrigin, propertyToken } from "./fixture-settings.mjs";
import { publishedSearchFixtures } from "./search-fixtures";
import { signInAs } from "./stack-identity";

test.use({ actionTimeout: 15000 });

test("published search preserves access uncertainty, calculated budgets and navigation across sign-in", async ({ page, browser, request }, testInfo) => {
  test.setTimeout(120000);
  const fixtures = await publishedSearchFixtures(request);
  const endpoint = "http://127.0.0.1:8000/published-listings";
  const initialQuery = new URLSearchParams({ town: fixtures.town, vehicle_access: "required" });
  const destination = "/buyer/search?" + initialQuery;
  const cards = page.getByTestId("search-card");
  async function apply(count: number) {
    await page.getByRole("button", { name: "Apply filters", exact: true }).click();
    await expect(cards).toHaveCount(count);
  }

  await test.step("verified seller publications and unauthenticated buyer search resume", async () => {
    const denied = await request.get(endpoint);
    expect(denied.status()).toBe(401);
    expect(denied.headers()["cache-control"]).toBe("no-store");
    await signInAs(page, destination, "buyer");
    await expect(page.getByRole("heading", { name: "Buyer search", exact: true })).toBeVisible();
    await expect(cards).toHaveCount(2);
    await expect(cards.nth(0)).toContainText(fixtures.land.headline);
    await expect(cards.nth(0)).toContainText("Vehicle access: Confirmed");
    await expect(cards.nth(1)).toContainText(fixtures.unknown.headline);
    await expect(cards.nth(1)).toContainText("Unknown — needs confirmation");
    await expect(page.getByRole("link", { name: fixtures.house.headline, exact: true })).toHaveCount(0);
    const refreshed = await page.reload();
    expect(refreshed?.headers()["cache-control"]).toContain("no-store");
    const result = await request.get(endpoint, { params: Object.fromEntries(initialQuery), headers: fixtures.buyer });
    expect(result.status()).toBe(200);
    expect(result.headers()["cache-control"]).toBe("no-store");
    const body = await result.json();
    expect(body.items.map((item: { listing_id: string }) => item.listing_id)).toEqual([fixtures.land.id, fixtures.unknown.id]);
    expect(body.items.map((item: { match_status: string }) => item.match_status)).toEqual(["matched", "needs_confirmation"]);
  });

  await test.step("listing search context survives an independent sign-in and Back to Search", async () => {
    const href = await page.getByRole("link", { name: fixtures.land.headline, exact: true }).getAttribute("href");
    expect(href).toContain("?search=");
    const fresh = await browser.newPage({ baseURL: appOrigin });
    try {
      await signInAs(fresh, href!, "buyer");
      await expect(fresh.getByRole("heading", { name: fixtures.land.headline, exact: true })).toBeVisible();
      await fresh.getByRole("link", { name: "Back to Search", exact: true }).click();
      await expect(fresh).toHaveURL(destination);
      await expect(fresh.getByLabel("Town", { exact: true })).toHaveValue(fixtures.town);
      await expect(fresh.getByRole("combobox", { name: "Vehicle access", exact: true })).toHaveValue("required");
      await expect(fresh.getByTestId("search-card")).toHaveCount(2);
    } finally { await fresh.close(); }
  });

  await test.step("vehicle modes, zero counts and private-data isolation", async () => {
    const mode = page.getByRole("combobox", { name: "Vehicle access", exact: true });
    await mode.selectOption("confirmed"); await apply(1);
    await expect(cards).toContainText(fixtures.land.headline);
    await mode.selectOption("none"); await apply(1);
    await expect(cards).toContainText(fixtures.house.headline);
    await expect(cards).toContainText("No vehicle access");
    await expect(cards.locator(".search-metrics div").filter({ hasText: "Bedrooms" })).toContainText("0");
    const previous = page.url();
    await page.getByRole("link", { name: fixtures.house.headline, exact: true }).click();
    await expect(page.getByText("Parking spaces", { exact: true }).locator("..").locator("dd")).toHaveText("0");
    await page.getByRole("link", { name: "Back to Search", exact: true }).click();
    await expect(page).toHaveURL(previous);
    await mode.selectOption("any"); await apply(3);
    await expect(page.getByRole("link", { name: fixtures.draft.headline, exact: true })).toHaveCount(0);
    const result = await request.get(endpoint, { params: { town: fixtures.town }, headers: fixtures.buyer });
    const json = await result.text();
    for (const secret of [fixtures.phone, fixtures.address, fixtures.location.latitude, fixtures.location.longitude,
      "private_details", "encrypted_value", fixtures.draft.id]) {
      expect(json).not.toContain(secret);
      expect(await page.content()).not.toContain(secret);
    }
    expect(await page.content()).not.toContain(propertyToken);
    const draft = await request.get(endpoint + "/" + fixtures.draft.id, { headers: fixtures.buyer });
    expect(draft.status()).toBe(404);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.screenshot({ path: testInfo.outputPath("search-all-desktop.png"), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth
      && Array.from(document.querySelectorAll('[data-testid="search-card"]')).every((card) => card.scrollWidth <= card.clientWidth))).toBeTruthy();
    await page.screenshot({ path: testInfo.outputPath("search-all-mobile.png"), fullPage: true });
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  await test.step("calculated land budgets and cross-unit measurement filters", async () => {
    await page.getByRole("combobox", { name: "Property type", exact: true }).selectOption("land");
    await page.getByLabel("Currency", { exact: true }).fill("LKR");
    await page.getByLabel("Maximum price", { exact: true }).fill("4500000"); await apply(0);
    await expect(page.getByText(/No published listings match these filters/)).toBeVisible();
    await page.getByLabel("Maximum price", { exact: true }).fill("5500000"); await apply(1);
    await expect(cards).toContainText("LKR 250,000 / perch");
    await expect(cards).toContainText("Approximate total: LKR 5,000,000");
    await page.getByLabel("Minimum price", { exact: true }).fill("5500000"); await apply(0);
    await page.getByLabel("Minimum price", { exact: true }).fill("");
    await page.getByLabel("Minimum land area", { exact: true }).fill("15");
    await page.getByRole("combobox", { name: "Land area unit", exact: true }).selectOption("perch"); await apply(1);
    await page.getByLabel("Minimum land area", { exact: true }).fill("21"); await apply(0);
    await page.getByLabel("Minimum land area", { exact: true }).fill("");
    await page.getByLabel("Maximum price", { exact: true }).fill("");
    await page.getByRole("combobox", { name: "Property type", exact: true }).selectOption("");
    await page.getByLabel("Minimum floor area", { exact: true }).fill("1000");
    await page.getByRole("combobox", { name: "Floor area unit", exact: true }).selectOption("sq_ft"); await apply(2);
    await page.getByLabel("Minimum floor area", { exact: true }).fill("1100"); await apply(1);
    await expect(cards).toContainText(fixtures.house.headline);
    await page.getByLabel("Minimum floor area", { exact: true }).fill("");
    await page.getByLabel("Minimum bedrooms", { exact: true }).fill("0"); await apply(1);
    await expect(cards).toContainText(fixtures.house.headline);
  });

  await test.step("pagination and exact result restoration", async () => {
    await page.goto("/buyer/search?" + new URLSearchParams({ town: fixtures.town, limit: "1" }));
    await expect(cards).toHaveCount(1);
    const firstId = await cards.getAttribute("data-listing-id");
    await page.getByRole("link", { name: "Next page", exact: true }).click();
    await expect(page).toHaveURL(/offset=1/);
    await expect(cards).toHaveCount(1);
    await expect(cards).not.toHaveAttribute("data-listing-id", firstId!);
    const secondId = await cards.getAttribute("data-listing-id");
    expect(secondId).not.toBe(firstId);
    const previous = page.url();
    await cards.getByRole("link").click();
    await page.getByRole("link", { name: "Back to Search", exact: true }).click();
    await expect(page).toHaveURL(previous);
    await expect(cards).toHaveAttribute("data-listing-id", secondId!);
  });
});
