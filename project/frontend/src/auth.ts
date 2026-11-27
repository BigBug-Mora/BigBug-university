import "server-only";

import NextAuth, { type Account } from "next-auth";
import Cognito from "next-auth/providers/cognito";
import { appOrigin, cognitoSettings, sessionSettings } from "@/server/config";
import { callbackFailures, returnDestination } from "@/server/destinations";
import { resolveAccount } from "@/server/engagement";

function providerSession(account: Account | null | undefined) {
  const accessToken = account?.access_token;
  const expiresAt = account?.expires_at;
  if (account?.provider === "cognito" && accessToken && typeof expiresAt === "number" && Number.isFinite(expiresAt)) {
    return { accessToken, expiresAt };
  }
}

export const { handlers, signIn, signOut } = NextAuth(() => {
  const { issuer, clientId, clientSecret } = cognitoSettings();
  const { secure, secret } = sessionSettings();
  const origin = appOrigin();
  return {
    secret,
    useSecureCookies: secure,
    providers: [
      Cognito({
        issuer,
        clientId,
        clientSecret,
        checks: ["pkce", "state", "nonce"],
        client: { token_endpoint_auth_method: "client_secret_basic" },
        authorization: { params: { scope: "openid", prompt: "login" } },
      }),
    ],
    session: { strategy: "jwt", maxAge: 8 * 60 * 60 },
    pages: { signIn: "/sign-in", error: "/sign-in" },
    logger: {
      error(error) {
        console.error("Auth.js request failed", "type" in error ? error.type : "Error");
      },
    },
    callbacks: {
      async signIn({ account }) {
        const session = providerSession(account);
        if (!session || session.expiresAt * 1000 <= Date.now()) return callbackFailures.expired;
        const { status } = await resolveAccount(session.accessToken);
        if (status === "active") return true;
        return callbackFailures[status === "unauthorized" ? "expired" : status];
      },
      jwt({ token, account }) {
        if (account) return providerSession(account) ?? null;
        return typeof token.expiresAt === "number" && token.expiresAt * 1000 > Date.now() ? token : null;
      },
      session({ session, token }) {
        return { expires: new Date(Math.min(Date.parse(session.expires), Number(token.expiresAt) * 1000)).toISOString() };
      },
      redirect({ url }) {
        const path = url.startsWith(`${origin}/`) ? url.slice(origin.length) : url;
        if (path === "/" || Object.values(callbackFailures).some((failure) => failure === path)) {
          return origin + path;
        }
        return origin + returnDestination(url, origin);
      },
    },
  };
});
