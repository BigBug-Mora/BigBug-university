import Link from "next/link";
import { endSession } from "@/app/actions";
import { protectedAccount } from "@/server/session";
import { sellerWorkspace } from "@/server/destinations";
import { propertyRequest } from "@/server/property";
import { Create } from "./create";

type Listing = { id: string; property_type: string; town: string | null; district: string | null; revision_no: number };

export default async function SellerPage() {
  const actor = await protectedAccount(sellerWorkspace);
  if (actor.status !== "active") return <h1>{actor.status === "forbidden" ? "Access denied" : "Service temporarily unavailable"}</h1>;
  const result = await propertyRequest<Listing[]>("");
  return <main className="workspace"><h1>Seller workspace</h1><p>Account <span>{actor.accountId}</span></p>
    <section><h2>Create a listing</h2><Create account={actor.accountId}/></section>
    <section><h2>Your drafts</h2>{!result.ok ? <p role="alert">{result.message}</p> : result.data.length ?
      <ul>{result.data.map(row => <li key={row.id}><Link href={sellerWorkspace+"/"+row.id}>
        {row.property_type} · {row.town ?? row.district ?? "Location unknown"} · Revision {row.revision_no}</Link></li>)}</ul> :
      <p>You have no saved drafts.</p>}</section><form action={endSession}><button className="button">Sign out</button></form></main>;
}
