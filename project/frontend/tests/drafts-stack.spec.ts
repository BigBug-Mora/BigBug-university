import { createHash, randomUUID } from "node:crypto";
import { expect, test, type APIRequestContext } from "@playwright/test";
import {
  callbackUrl,
  clientId,
  clientSecret,
  propertyToken,
} from "./fixture-settings.mjs";

const provider = "http://127.0.0.1:47121";
const property = "http://127.0.0.1:8000/listings";

async function credentials(request: APIRequestContext, identity: string) {
  const verifier = randomUUID() + randomUUID();
  const login = await request.get(provider + "/authorize", {
    params: {
      client_id: clientId,
      redirect_uri: callbackUrl,
      scope: "openid",
      response_type: "code",
      prompt: "login",
      code_challenge_method: "S256",
      code_challenge: createHash("sha256").update(verifier).digest("base64url"),
      state: randomUUID(),
      nonce: randomUUID(),
    },
  });
  const id = /finish\?id=([a-f0-9-]+)/.exec(await login.text())?.[1];
  if (!id) throw new Error("Fixture authorization unavailable");
  const approved = await request.get(provider + "/finish", {
    params: { id, approve: "1", identity },
    maxRedirects: 0,
  });
  const code = new URL(approved.headers().location).searchParams.get("code")!;
  const token = await request.post(provider + "/token", {
    headers: {
      Authorization:
        "Basic " +
        Buffer.from(clientId + ":" + clientSecret).toString("base64"),
    },
    form: {
      code,
      code_verifier: verifier,
      grant_type: "authorization_code",
      redirect_uri: callbackUrl,
    },
  });
  expect(token.ok()).toBeTruthy();
  return {
    Authorization: "Bearer " + (await token.json()).access_token,
    "X-EstateFlow-Service-Token": propertyToken,
  };
}

test("seller reopens drafts, retries revisions and retires private details across account boundaries", async ({
  page,
  request,
}) => {
  test.setTimeout(120000);
  const seller = await credentials(request, "seller");
  const other = await credentials(request, "buyer");
  await page.goto("/seller/workspace");
  await page.getByRole("button", { name: "Sign in with Cognito" }).click();
  await page.getByRole("link", { name: "Approve as seller" }).click();
  for (const type of ["apartment", "land", "house"]) {
    await page.getByLabel("Property type").selectOption(type);
    await page.getByRole("button", { name: "Create draft" }).click();
    await expect(
      page.getByRole("heading", { name: type + " draft", exact: true }),
    ).toBeVisible();
    if (type === "land") {
      await page.getByLabel("Price basis").selectOption("per_unit");
      await page.getByLabel("Entered price").fill("25000");
      await page.getByLabel("Currency").fill("LKR");
      await page.getByLabel("Price area unit").selectOption("perch");
    }
    await page.getByLabel("Parking spaces", { exact: true }).fill("0");
    await page.getByLabel("Vehicle access").selectOption("false");
    await page.getByRole("button", { name: "Save draft", exact: true }).click();
    await expect(page.getByText("Draft saved.", { exact: true })).toBeVisible();
    await page.reload();
    await expect(
      page.getByLabel("Parking spaces", { exact: true }),
    ).toHaveValue("0");
    await expect(page.getByLabel("Vehicle access")).toHaveValue("false");
    await expect(page.getByLabel("Covered parking spaces")).toHaveValue("");
    if (type === "land")
      await expect(page.getByLabel("Price area unit")).toHaveValue("perch");
    if (type !== "house")
      await page
        .getByRole("link", { name: "Back to seller workspace" })
        .click();
  }
  const url = property + "/" + new URL(page.url()).pathname.split("/").pop();
  const details = url + "/private-details";
  async function phoneId() {
    const rows = await (await request.get(details, { headers: seller })).json();
    return rows.find(
      (r: { detail_kind: string; retired_at: string | null }) =>
        r.detail_kind === "phone" && !r.retired_at,
    )?.id;
  }
  const phone = page.getByLabel("Phone 1", { exact: true });
  await phone.fill("+15550101111");
  await page.getByRole("button", { name: "Save phone 1", exact: true }).click();
  const remove = page.getByRole("button", { name: "Remove phone 1" });
  await expect(remove).toBeVisible();
  const old = await phoneId();
  await phone.fill("+15550102222");
  await page.getByRole("button", { name: "Save phone 1", exact: true }).click();
  await expect(page.getByText("Detail saved.", { exact: true })).toBeVisible();
  expect(await phoneId()).toBe(old);
  await remove.click();
  await expect(remove).toHaveCount(0);
  await phone.fill("+15550103333");
  await page.getByRole("button", { name: "Save phone 1", exact: true }).click();
  await expect(remove).toBeVisible();
  expect(await phoneId()).not.toBe(old);
  await page.reload();
  await expect(phone).toHaveValue("+15550103333");
  for (const name of ["written address", "map pin"]) {
    const address = page.getByLabel("Written address", { exact: true });
    if (name === "written address") await address.fill("17 Fictional Lane");
    else {
      await page.getByLabel("Latitude").fill("0");
      await page.getByLabel("Longitude").fill("80");
    }
    await page.getByRole("button", { name: "Save " + name }).click();
    const removeDetail = page.getByRole("button", { name: "Remove " + name });
    await expect(removeDetail).toBeVisible();
    await page.reload();
    if (name === "written address") await expect(address).toHaveValue("17 Fictional Lane");
    else await expect(page.getByLabel("Latitude")).toHaveValue("0");
    await removeDetail.click();
    await expect(removeDetail).toHaveCount(0);
  }
  const current = await (await request.get(url, { headers: seller })).json();
  const data = {
    edit_action_id: randomUUID(),
    parent_revision_id: current.revision.id,
    draft: {
      property_type: "house",
      town: "Test town",
      parking_spaces: 0,
      vehicle_access: false,
    },
  };
  const saved = await request.post(url + "/revisions", {
    headers: seller,
    data,
  });
  expect(saved.status()).toBe(200);
  const retry = await request.post(url + "/revisions", {
    headers: seller,
    data,
  });
  expect(await retry.json()).toEqual(await saved.json());
  await page.getByLabel("Town", { exact: true }).fill("Unsaved local town");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("link", { name: "Open current revision" })).toBeVisible();
  await expect(page.getByLabel("Town", { exact: true })).toHaveValue("Unsaved local town");
  for (const response of [
    await request.get(url, { headers: other }),
    await request.post(url + "/revisions", { headers: other, data }),
    await request.get(details, { headers: other }),
    await request.put(details + "/phone/1", {
      headers: other,
      data: { value: "+15550104444" },
    }),
    await request.delete(details + "/" + old, { headers: other }),
  ]) {
    expect(response.status()).toBe(404);
    expect(await response.json()).toEqual({ detail: "Listing unavailable" });
  }
});
