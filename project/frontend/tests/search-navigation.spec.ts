import { expect, test } from "@playwright/test";
import { buyerReturnPath, listingSearchHref, searchHref, searchState, validatedSearchQuery } from "../src/lib/search-navigation";
import { measurement, money } from "../src/components/listing-format";

const listingId = "12345678-1234-4234-8234-123456789abc";

test("search criteria round-trip through listing and sign-in return URLs", () => {
  const state = searchState({ property_type: "land", town: "50% & _ Court", max_price: "5500000",
    min_land_area: "15", land_area_unit: "perch", vehicle_access: "required" });
  expect(state.valid).toBe(true);
  expect(state.request.get("currency")).toBe("LKR");
  expect(state.request.get("town")).toBe("50% & _ Court");
  const href = listingSearchHref(listingId, state.query);
  const context = new URL(href, "https://estateflow.invalid").searchParams.get("search");
  expect(context).toBe(state.query);
  expect(buyerReturnPath(href)).toBe(href);
  expect(buyerReturnPath(searchHref(state.query))).toBe(searchHref(state.query));
  expect(searchHref(context)).toBe("/buyer/search?" + state.query);
  const blanks = searchState({ town: "", land_area_unit: "perch", floor_area_unit: "sq_m", min_price: "" });
  expect(blanks.request.toString()).toBe("");
});

test("search navigation rejects hostile or ambiguous context and unsafe listing IDs", () => {
  for (const token of ["https://outside.invalid", "//outside.invalid", "/buyer/search?town=x", "town=a&town=b",
    "returnTo=https://outside.invalid", "town=x%0Ay", "town=x#fragment", "town=" + "a".repeat(161)]) {
    expect(validatedSearchQuery(token)).toBeUndefined();
    expect(searchHref(token)).toBe("/buyer/search");
    expect(buyerReturnPath(`/buyer/listings/${listingId}?search=${encodeURIComponent(token)}`)).toBeUndefined();
  }
  expect(searchState({ town: ["a", "b"] }).valid).toBe(false);
  expect(buyerReturnPath(`/buyer/listings/${listingId}?search=town%3Da&search=town%3Db`)).toBeUndefined();
  expect(buyerReturnPath("/buyer/search/../seller/workspace")).toBeUndefined();
  expect(listingSearchHref("//outside.invalid", "town=x")).toBe("/buyer/search");
});

test("published prices retain decimal precision and measurements retain their qualifiers", () => {
  expect(money("9999999999999999.99", "LKR")).toBe("LKR 9,999,999,999,999,999.99");
  expect(money("5000000.00", "LKR")).toBe("LKR 5,000,000");
  expect(money("12.345", "USD")).toBe("USD 12.35");
  expect(money(null, "LKR")).toBe("Price not provided");
  expect(measurement("12.000000", "perch", true)).toBe("Approx. 12 perch");
});
