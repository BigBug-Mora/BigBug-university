"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { signIn, signOut } from "@/auth";
import { appOrigin, cognitoSettings, sessionSettings } from "@/server/config";
import { returnDestination } from "@/server/destinations";

export async function beginSignIn(formData: FormData) {
  const destination = returnDestination(formData.get("returnTo"), appOrigin());
  await signIn("cognito", { redirectTo: destination });
}

export async function endSession() {
  const { loginOrigin, clientId } = cognitoSettings();
  const logout = new URL("/logout", loginOrigin);
  logout.searchParams.set("client_id", clientId);
  logout.searchParams.set("logout_uri", `${appOrigin()}/`);

  await signOut({ redirect: false, redirectTo: "/" });
  (await cookies()).delete(sessionSettings().callbackCookie);
  redirect(logout.toString());
}
