export function label(value: string) {
  const text = value.replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function scalar(value: unknown): string {
  if (value === null || value === undefined || value === "") return "Unknown";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return typeof value === "string" || typeof value === "number" ? String(value) : "Unknown";
}

export function measurement(value: unknown, unit: unknown, approximate: unknown) {
  if (value === null || value === undefined) return "Unknown";
  const amount = scalar(value).replace(/(\.\d*?[1-9])0+$|\.0+$/, "$1");
  return `${approximate === true ? "Approx. " : ""}${amount}${unit ? ` ${scalar(unit).replaceAll("_", " ")}` : ""}`;
}

export function money(value: unknown, currency: unknown) {
  if (value === null || value === undefined) return "Price not provided";
  const number = Number(value);
  return `${scalar(currency)} ${Number.isFinite(number) ? new Intl.NumberFormat("en-LK", { maximumFractionDigits: 2 }).format(number) : scalar(value)}`;
}

// Preview-only display conversion; buyer totals always come from Property's public view.
const squareMetres: Record<string, number> = {
  sq_m: 1, sq_ft: 0.09290304, perch: 25.29285264, acre: 4046.8564224, hectare: 10000,
};
export function previewTotal(listing: Record<string, unknown>) {
  if (listing.price_basis !== "per_unit") return listing.entered_price;
  const land = squareMetres[String(listing.land_area_unit)];
  const price = squareMetres[String(listing.price_area_unit)];
  if (!land || !price || listing.land_area == null || listing.entered_price == null) return null;
  return Number(listing.entered_price) * Number(listing.land_area) * land / price;
}
