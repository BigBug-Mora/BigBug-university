import "server-only";

import { engagementSettings } from "./config";

type Resolution =
  | { status: "active"; accountId: string }
  | { status: "unauthorized" | "forbidden" | "unavailable" };

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function resolveAccount(accessToken: string): Promise<Resolution> {
  try {
    const { origin, serviceToken } = engagementSettings();
    const response = await fetch(new URL("/internal/accounts/resolve", origin), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "X-EstateFlow-Service-Token": serviceToken,
      },
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(3000),
    });
    if (response.status === 401) return { status: "unauthorized" };
    if (response.status === 403) return { status: "forbidden" };
    if (response.status === 200) {
      const result = await response.json();
      if (typeof result?.account_id === "string" && uuid.test(result.account_id)) {
        return { status: "active", accountId: result.account_id };
      }
    }
  } catch {
    // Keep backend responses, credentials and token claims out of logs.
  }
  return { status: "unavailable" };
}
