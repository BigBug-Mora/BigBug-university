import "server-only";

import { getToken } from "next-auth/jwt";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { sessionSettings } from "./config";
import { verifyPropertyAccount } from "./account-api";

export async function sessionToken() {
  const request = await headers();
  const { secret, secure, sessionCookie } = sessionSettings();
  const token = await getToken({
    req: { headers: new Headers({ cookie: request.get("cookie") ?? "" }) },
    secret,
    secureCookie: secure,
    cookieName: sessionCookie,
  });
  return token;
}

export async function protectedAccount(destination: string) {
  const token = await sessionToken();
  const signIn = `/sign-in?returnTo=${encodeURIComponent(destination)}`;
  if (!token || typeof token.accessToken !== "string" || typeof token.expiresAt !== "number") {
    redirect(signIn);
  }
  if (token.expiresAt * 1000 <= Date.now()) redirect(`${signIn}&status=expired`);

  const account = await verifyPropertyAccount(token.accessToken);
  if (account.status === "unauthorized") redirect(`${signIn}&status=expired`);
  return account;
}
