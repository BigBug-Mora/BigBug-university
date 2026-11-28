import { randomUUID } from "node:crypto";
import { expect, type APIRequestContext } from "@playwright/test";
import { propertyCredentials } from "./stack-identity";

const property = "http://127.0.0.1:8000";

export async function publishedSearchFixtures(request: APIRequestContext) {
  const seller = await propertyCredentials(request, "seller");
  const buyer = await propertyCredentials(request, "buyer");
  const tag = randomUUID().slice(0, 8);
  const town = `Search ${tag} 100%_!`;
  const phone = "+15550107777";
  const address = `Private Search Address ${tag}`;
  const location = { latitude: "6.765432", longitude: "80.876543" };
  async function listing(kind: string, facts: Record<string, unknown>, publish = true) {
    const created = await request.post(property + "/listings", { headers: seller, data: {
      create_action_id: randomUUID(), draft: { property_type: kind, district: "Fictional Search District", town,
        price_basis: "total", entered_price: "3000000", currency: "LKR", ...facts },
    } });
    expect(created.status()).toBe(200);
    const draft = await created.json();
    const path = `${property}/listings/${draft.listing_id}`;
    const savedPhone = await request.put(path + "/private-details/phone/1", { headers: seller, data: { value: phone } });
    expect(savedPhone.status()).toBe(200);
    if (kind === "house") {
      for (const [slot, value] of [["written_address/1", address], ["map_pin/1", location]] as const) {
        expect((await request.put(path + "/private-details/" + slot, { headers: seller, data: { value } })).status()).toBe(200);
      }
    }
    const headline = `${publish ? "Search" : "Unpublished"} ${kind} ${tag}`;
    const authored = await request.post(path + "/showcases", { headers: seller, data: {
      action_id: randomUUID(), source_revision_id: draft.revision.id, headline,
      description: "Fictional seller-authored search acceptance listing.", highlights: ["Seller-stated facts available"],
    } });
    expect(authored.status()).toBe(200);
    if (publish) {
      const result = await request.post(path + "/publish", { headers: seller, data: {
        action_id: randomUUID(), listing_revision_id: draft.revision.id, showcase_id: (await authored.json()).id,
      } });
      expect(result.status()).toBe(200);
    }
    return { id: draft.listing_id as string, headline };
  }
  const land = await listing("land", { vehicle_access: true, price_basis: "per_unit", entered_price: "250000",
    price_area_unit: "perch", land_area: "0.125", land_area_unit: "acre", land_area_approximate: true });
  const house = await listing("house", { vehicle_access: false, bedroom_count: 0, bathroom_count: 0,
    parking_spaces: 0, land_area: "10", land_area_unit: "perch", floor_area: "1200", floor_area_unit: "sq_ft" });
  const unknown = await listing("apartment", { vehicle_access: null, floor_area: "100", floor_area_unit: "sq_m", entered_price: "4000000" });
  const draft = await listing("land", { vehicle_access: true }, false);
  return { town, phone, address, location, land, house, unknown, draft, buyer };
}
