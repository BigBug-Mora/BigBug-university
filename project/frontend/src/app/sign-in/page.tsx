import Link from "next/link";
import { cookies } from "next/headers";
import { beginSignIn } from "@/app/actions";
import { appOrigin, sessionSettings } from "@/server/config";
import { returnDestination } from "@/server/destinations";

const messages = {
  expired: ["Session expired", "Sign in again to continue where you left off."],
  forbidden: ["Access denied", "This account cannot access EstateFlow. You can sign in with another account."],
  unavailable: ["Service temporarily unavailable", "Try signing in again in a moment."],
} as const;

export default async function SignInPage({
  searchParams,
}: {
  searchParams: Promise<{ returnTo?: string | string[]; status?: string | string[]; error?: string | string[] }>;
}) {
  const { returnTo, status, error } = await searchParams;
  const previous = status || error ? (await cookies()).get(sessionSettings().callbackCookie)?.value : undefined;
  const destination = returnDestination(returnTo ?? previous, appOrigin());
  const message = status === "expired" || status === "forbidden" || status === "unavailable"
    ? messages[status]
    : error ? ["Sign-in could not be completed", "You can try signing in again."]
      : ["Sign in", "Sign in to continue to the requested page."];

  return (
    <div className="space-y-7">
      <h1>{message[0]}</h1>
      <p>{message[1]}</p>
      <div className="flex flex-wrap items-center gap-4">
        <form action={beginSignIn}>
          <input type="hidden" name="returnTo" value={destination} />
          <button type="submit" className="button button-primary">Sign in with Cognito</button>
        </form>
        <Link href="/" className="underline underline-offset-4">Back to home</Link>
      </div>
    </div>
  );
}
