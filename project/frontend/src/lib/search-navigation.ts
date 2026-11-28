/** URL safety and form transport; Property owns domain filter validation. */
export const searchKeys = [
  "property_type", "district", "town", "currency", "min_price", "max_price",
  "min_bedrooms", "min_bathrooms", "min_land_area", "land_area_unit",
  "min_floor_area", "floor_area_unit", "vehicle_access", "limit", "offset",
] as const;
export type SearchFilters = Partial<Record<typeof searchKeys[number], string>>;
const allowed = new Set<string>(searchKeys);
const uuid = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;

export function validatedSearchQuery(value: unknown): string | undefined {
  if (typeof value !== "string" || value.length > 4096 || /^[?/#]/.test(value) || value.includes("#")) return;
  const params = new URLSearchParams(value);
  const seen = new Set<string>();
  for (const [key, text] of params) {
    if (!allowed.has(key) || seen.has(key) || text.length > 160 || /[\u0000-\u001f\u007f]/.test(text)) return;
    seen.add(key);
  }
  return params.toString();
}

export function searchHref(query: unknown = "") {
  const checked = validatedSearchQuery(query);
  return "/buyer/search" + (checked ? "?" + checked : "");
}

export function listingSearchHref(listingId: string, query: unknown = "") {
  if (!uuid.test(listingId)) return "/buyer/search";
  const checked = validatedSearchQuery(query);
  return `/buyer/listings/${listingId}` + (checked ? "?search=" + encodeURIComponent(checked) : "");
}

export function buyerReturnPath(path: string): string | undefined {
  if (path === "/buyer/search") return path;
  if (path.startsWith("/buyer/search?")) {
    const checked = validatedSearchQuery(path.slice("/buyer/search?".length));
    return checked === undefined ? undefined : searchHref(checked);
  }
  const match = /^\/buyer\/listings\/([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})(?:\?(.*))?$/i.exec(path);
  if (!match) return;
  if (match[2] === undefined) return listingSearchHref(match[1]);
  const params = new URLSearchParams(match[2]);
  if (Array.from(params.keys()).some((key) => key !== "search") || params.getAll("search").length !== 1) return;
  const checked = validatedSearchQuery(params.get("search"));
  return checked === undefined ? undefined : listingSearchHref(match[1], checked);
}

export function searchState(raw: Record<string, string | string[] | undefined>) {
  const params = new URLSearchParams();
  let valid = true;
  for (const [key, value] of Object.entries(raw)) {
    if (Array.isArray(value)) valid = false;
    else if (value !== undefined) params.append(key, value);
  }
  const checked = valid ? validatedSearchQuery(params.toString()) : undefined;
  const request = new URLSearchParams(checked ?? "");
  for (const [key, value] of Array.from(request)) {
    if (!value.trim()) request.delete(key);
    else request.set(key, value.trim());
  }
  for (const dimension of ["land", "floor"]) {
    if (!request.has(`min_${dimension}_area`)) request.delete(`${dimension}_area_unit`);
  }
  if (request.has("currency")) request.set("currency", request.get("currency")!.toUpperCase());
  else if (request.has("min_price") || request.has("max_price")) request.set("currency", "LKR");
  return { valid: checked !== undefined, query: checked ?? "", request,
    filters: Object.fromEntries(request) as SearchFilters };
}

export function pageHref(query: string, offset: number) {
  const params = new URLSearchParams(validatedSearchQuery(query) ?? "");
  params.set("offset", String(offset));
  return searchHref(params.toString());
}
