import { endSession } from "@/app/actions";
import { protectedAccount } from "@/server/session";

export async function ProtectedView({
  destination,
  title,
}: {
  destination: string;
  title: string;
}) {
  const account = await protectedAccount(destination);
  let heading = title;
  let description: React.ReactNode;

  if (account.status === "active") {
    description = <p>Account <span className="break-all font-mono">{account.accountId}</span></p>;
  } else if (account.status === "forbidden") {
    heading = "Access denied";
    description = <p>This account cannot access EstateFlow.</p>;
  } else {
    heading = "Service temporarily unavailable";
    description = <p>Reload this page to try again.</p>;
  }

  return (
    <div className="space-y-7">
      <h1>{heading}</h1>
      {description}
      <form action={endSession}>
        <button type="submit" className="button">Sign out</button>
      </form>
    </div>
  );
}
