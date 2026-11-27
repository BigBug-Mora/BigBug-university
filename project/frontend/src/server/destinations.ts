import "server-only";

export const buyerSearch = "/buyer/search";
export const sellerWorkspace = "/seller/workspace";

export function listingPath(id: string): string | undefined {
  if (/^[a-zA-Z0-9][a-zA-Z0-9-]{0,63}$/.test(id)) return `/buyer/listings/${id}`;
}

export function returnDestination(value: unknown, origin: string): string {
  if (typeof value !== "string") return buyerSearch;
  const path = value.startsWith(`${origin}/`) ? value.slice(origin.length) : value;
  if (path === sellerWorkspace || path === buyerSearch) return path;
  if (/^\/seller\/workspace\/[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(path)) return path;
  const id = path.startsWith("/buyer/listings/") ? path.slice("/buyer/listings/".length) : "";
  return listingPath(id) ?? buyerSearch;
}

export const callbackFailures = {
  forbidden: "/sign-in?status=forbidden",
  unavailable: "/sign-in?status=unavailable",
  expired: "/sign-in?status=expired",
} as const;
