import { expect, test } from "@playwright/test";
import { signInAs } from "./stack-identity";

test.use({ actionTimeout: 15000 });

test("search controls render the published plot and restore its query from the listing", async ({ page }, testInfo) => {
  await signInAs(page, "/buyer/search", "buyer");
  await expect(page.getByRole("heading", { name: "Buyer search", exact: true })).toBeVisible();
  await page.getByRole("combobox", { name: "Property type", exact: true }).selectOption("land");
  await page.getByLabel("Town", { exact: true }).fill("Example Town");
  await page.getByLabel("Maximum price", { exact: true }).fill("5500000");
  await page.getByLabel("Minimum land area", { exact: true }).fill("15");
  await page.getByRole("combobox", { name: "Vehicle access", exact: true }).selectOption("confirmed");
  await page.getByRole("button", { name: "Apply filters" }).click();
  await expect(page.getByTestId("search-card")).toHaveCount(1);
  await expect(page.getByLabel("Currency", { exact: true })).toHaveValue("LKR");
  await expect(page.getByTestId("search-card")).toContainText("Approximate total: LKR 5,000,000");
  await expect(page.getByTestId("search-card")).toContainText("Confirmed");
  const destination = page.url();
  await page.screenshot({ path: testInfo.outputPath("search-desktop.png"), fullPage: true });
  await page.getByRole("link", { name: "Example Town Plot", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Example Town Plot", exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Back to Search", exact: true }).click();
  await expect(page).toHaveURL(destination);
  await expect(page.getByLabel("Town", { exact: true })).toHaveValue("Example Town");
  await expect(page.getByLabel("Maximum price", { exact: true })).toHaveValue("5500000");
  await expect(page.getByTestId("search-card")).toHaveCount(1);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.screenshot({ path: testInfo.outputPath("search-mobile.png"), fullPage: true });
  await page.getByRole("link", { name: "Clear filters", exact: true }).click();
  await expect(page).toHaveURL("/buyer/search");
  await expect(page.getByLabel("Town", { exact: true })).toHaveValue("");
});
