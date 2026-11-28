import "server-only";
import { propertySettings } from "./config";
import { sessionToken } from "./session";
import type { SearchResults } from "@/components/search/types";

export type Result<T> =
  { ok: true; data: T } | { ok: false; status: number; message: string };

const errors: Record<number, string> = {
  401: "Your session expired. Sign in again to continue.",
  403: "Access denied.",
  404: "This draft is unavailable to your account.",
  409: "Another revision was saved. Reopen the draft to review the current values.",
  422: "Check the field values, related counts, prices and units.",
};

async function callProperty<T>(
  path: string,
  method = "GET",
  body?: unknown,
  notFoundMessage = errors[404],
  forwardDetail = false,
): Promise<Result<T>> {
  const session = await sessionToken();
  if (
    typeof session?.accessToken !== "string" ||
    typeof session.expiresAt !== "number" ||
    session.expiresAt * 1000 <= Date.now()
  ) {
    return { ok: false, status: 401, message: errors[401] };
  }
  try {
    const { origin, serviceToken } = propertySettings();
    const response = await fetch(origin + path, {
      method,
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(10000),
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
        "X-EstateFlow-Service-Token": serviceToken,
        "Content-Type": "application/json",
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (response.ok)
      return {
        ok: true,
        data: response.status === 204 ? null : await response.json(),
      };
    let message =
      response.status === 404
        ? notFoundMessage
        : (errors[response.status] ?? "Property service unavailable. Try again.");
    if (response.status === 409 && path.includes("/private-details/"))
      message = "This phone number already occupies another slot.";
    if (forwardDetail && (response.status === 409 || response.status === 422)) {
      const payload = await response.json().catch(() => null);
      if (typeof payload?.detail === "string" && payload.detail.trim()) {
        message = payload.detail;
      }
    }
    return { ok: false, status: response.status, message };
  } catch {
    return {
      ok: false,
      status: 503,
      message: "The service could not confirm the request. Try again.",
    };
  }
}

export function propertyRequest<T>(
  path: string,
  method = "GET",
  body?: unknown,
  forwardDetail = false,
): Promise<Result<T>> {
  return callProperty<T>(
    "/listings" + path,
    method,
    body,
    errors[404],
    forwardDetail,
  );
}

export function publishedPropertyRequest<T>(
  listingId: string,
): Promise<Result<T>> {
  return callProperty<T>(
    "/published-listings/" + listingId,
    "GET",
    undefined,
    "Listing unavailable.",
  );
}

export function searchPublishedListings(params: URLSearchParams): Promise<Result<SearchResults>> {
  const query = params.toString();
  return callProperty<SearchResults>("/published-listings" + (query ? "?" + query : ""));
}
