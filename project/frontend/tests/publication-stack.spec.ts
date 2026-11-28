import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";
import { appOrigin } from "./fixture-settings.mjs";
import { propertyCredentials, signInAs } from "./stack-identity";

const property = "http://127.0.0.1:8000";
test.use({ actionTimeout: 15000 });

test("seller publication isolates private price edits until a matching updated pair is published", async ({ page, browser, request }) => {
  test.setTimeout(90000);
  const sellerHeaders = await propertyCredentials(request, "seller");
  const buyerHeaders = await propertyCredentials(request, "buyer");
  await signInAs(page, "/seller/workspace", "seller");
  await page.getByRole("button", { name: "Create draft", exact: true }).click();
  await expect(page.getByRole("heading", { name: "house draft", exact: true })).toBeVisible();
  const editor = new URL(page.url()).pathname;
  const listingId = editor.split("/").pop()!;
  const listingPath = `/buyer/listings/${listingId}`;
  const api = `${property}/listings/${listingId}`;
  await page.getByLabel("District", { exact: true }).fill("Fictional District");
  await page.getByLabel("Town", { exact: true }).fill("Courtyard Town");
  await page.getByRole("combobox", { name: "Price basis", exact: true }).selectOption("total");
  await page.getByLabel("Entered price", { exact: true }).fill("15000000");
  await page.getByLabel("Currency", { exact: true }).fill("LKR");
  await page.getByLabel("Land area", { exact: true }).fill("12");
  await page.getByRole("combobox", { name: "Land area unit", exact: true }).selectOption("perch");
  await page.getByLabel("Bedroom count", { exact: true }).fill("3");
  await page.getByLabel("Bathroom count", { exact: true }).fill("2");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByText("Draft saved.", { exact: true })).toBeVisible();
  await page.getByLabel("Phone 1", { exact: true }).fill("+15550102222");
  await page.getByRole("button", { name: "Save phone 1", exact: true }).click();
  await expect(page.getByRole("button", { name: "Remove phone 1", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Apply authored starter" }).click();
  await page.getByLabel("Headline", { exact: true }).fill("Courtyard House publication check");
  await page.getByRole("button", { name: "Save showcase", exact: true }).click();
  await expect(page.getByText("Ready to publish this revision and showcase.")).toBeVisible();
  await page.getByRole("link", { name: "Preview showcase", exact: true }).click();
  await expect(page.getByText("Seller preview · Not a publication")).toBeVisible();
  await page.getByRole("button", { name: "Publish listing", exact: true }).click();
  await expect(page.getByText("Listing published.", { exact: true })).toBeVisible();

  const buyer = await browser.newPage({ baseURL: appOrigin, viewport: { width: 1280, height: 800 } });
  try {
    // An independent unauthenticated browser resumes this exact UUID listing after sign-in.
    await signInAs(buyer, listingPath, "buyer");
    await expect(buyer.getByRole("heading", { name: "Courtyard House publication check" })).toBeVisible();
    await expect(buyer.getByTestId("asking-price")).toHaveText("LKR 15,000,000");
    await expect(buyer.getByText("No photos published yet")).toBeVisible();
    await expect(buyer.locator("article img")).toHaveCount(0);
    const originalResponse = await request.get(property + "/published-listings/" + listingId, { headers: buyerHeaders });
    expect(originalResponse.status()).toBe(200);
    expect(originalResponse.headers()["cache-control"]).toBe("no-store");
    const original = await originalResponse.json();
    expect(original.entered_price).toBe("15000000.00");

    await page.goto(editor);
    await page.getByLabel("Entered price", { exact: true }).fill("18000000");
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(page.getByText("Draft saved.", { exact: true })).toBeVisible();
    await expect(page.getByText(/showcase is based on an earlier revision/)).toBeVisible();
    const refresh = await buyer.reload();
    expect(refresh?.headers()["cache-control"]).toContain("no-store");
    await expect(buyer.getByTestId("asking-price")).toHaveText("LKR 15,000,000");
    expect(await (await request.get(property + "/published-listings/" + listingId, { headers: buyerHeaders })).json()).toEqual(original);

    const previewResponse = await request.get(api + "/showcase", { headers: sellerHeaders });
    expect(previewResponse.status()).toBe(200);
    const preview = await previewResponse.json();
    expect(preview.showcase_matches_draft).toBe(false);
    const rejected = await request.post(api + "/publish", { headers: sellerHeaders, data: {
      action_id: randomUUID(), listing_revision_id: preview.revision.id, showcase_id: preview.showcase.id,
    } });
    expect(rejected.status()).toBe(409);
    await page.getByRole("button", { name: "Publish listing", exact: true }).click();
    await expect(page.getByText("Publish the current draft with a matching showcase. Reopen the preview.")).toBeVisible();
    await buyer.reload();
    await expect(buyer.getByTestId("asking-price")).toHaveText("LKR 15,000,000");

    await page.getByLabel("Headline", { exact: true }).fill("Courtyard House updated publication");
    await page.getByRole("button", { name: "Save showcase", exact: true }).click();
    await expect(page.getByText("Ready to publish this revision and showcase.")).toBeVisible();
    await page.getByRole("link", { name: "Preview showcase", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Courtyard House updated publication" })).toBeVisible();
    await expect(page.getByTestId("asking-price")).toHaveText("LKR 18,000,000");
    await page.getByRole("button", { name: "Publish listing", exact: true }).click();
    await expect(page.getByText("Listing published.", { exact: true })).toBeVisible();
    await buyer.reload();
    await expect(buyer.getByRole("heading", { name: "Courtyard House updated publication" })).toBeVisible();
    await expect(buyer.getByTestId("asking-price")).toHaveText("LKR 18,000,000");
    await expect(buyer.getByText("+15550102222", { exact: true })).toHaveCount(0);
    const latest = await (await request.get(property + "/published-listings/" + listingId, { headers: buyerHeaders })).json();
    expect(latest.listing_revision_id).toBe(preview.revision.id);
    expect(latest.showcase_id).not.toBe(original.showcase_id);
    expect(latest.entered_price).toBe("18000000.00");
  } finally {
    await buyer.close();
  }
});

test("buyers cannot read unpublished listings or use the standalone slug in the real stack", async ({ page, request }) => {
  const seller = await propertyCredentials(request, "seller");
  const buyer = await propertyCredentials(request, "buyer");
  const created = await request.post(property + "/listings", { headers: seller,
    data: { create_action_id: randomUUID(), draft: { property_type: "land" } } });
  expect(created.status()).toBe(200);
  const { listing_id: listingId } = await created.json();
  const endpoint = property + "/published-listings/" + listingId;
  const unauthorized = await request.get(endpoint);
  expect(unauthorized.status()).toBe(401);
  expect(unauthorized.headers()["cache-control"]).toBe("no-store");
  const unpublished = await request.get(endpoint, { headers: buyer });
  expect(unpublished.status()).toBe(404);
  expect(await unpublished.json()).toEqual({ detail: "Listing unavailable" });
  expect(unpublished.headers()["cache-control"]).toBe("no-store");
  await signInAs(page, `/buyer/listings/${listingId}`, "buyer");
  await expect(page.getByRole("heading", { name: "Listing unavailable" })).toBeVisible();
  const malformed = await request.get(property + "/published-listings/courtyard-house", { headers: buyer });
  expect(malformed.status()).toBe(422);
  await page.goto("/buyer/listings/courtyard-house");
  await expect(page.getByRole("heading", { name: "Listing unavailable" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Listing courtyard-house" })).toHaveCount(0);
});
