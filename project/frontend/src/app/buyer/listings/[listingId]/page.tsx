import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { ProtectedView } from "@/app/protected-view";
import { endSession } from "@/app/actions";
import { ListingShowcase } from "@/components/listing-showcase";
import type { ListingView } from "@/components/listing-types";
import { protectedAccount } from "@/server/session";
import { publishedPropertyRequest } from "@/server/property";
import { listingSearchHref, searchHref, validatedSearchQuery } from "@/lib/search-navigation";

export default async function ListingPage({ params, searchParams }: {
  params: Promise<{ listingId: string }>;
  searchParams: Promise<{ search?: string | string[] }>;
}) {
  const { listingId } = await params;
  const query = validatedSearchQuery((await searchParams).search) ?? "";
  const destination = listingSearchHref(listingId, query);
  // Only the standalone OIDC fixture enables this compatibility page.
  if (listingId === "courtyard-house" && process.env.ESTATEFLOW_TEST_STANDALONE_FIXTURES === "1"
      && process.env.ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER === "1") {
    return <ProtectedView destination="/buyer/listings/courtyard-house" title="Listing courtyard-house" />;
  }
  const actor = await protectedAccount(destination);
  if (actor.status !== "active") return <h1>{actor.status === "forbidden" ? "Access denied" : "Service temporarily unavailable"}</h1>;
  if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(listingId)) notFound();
  const result = await publishedPropertyRequest<ListingView>(listingId);
  if (!result.ok) {
    if (result.status === 401) redirect(`/sign-in?returnTo=${encodeURIComponent(destination)}&status=expired`);
    if (result.status === 404) notFound();
    return <div><h1>Service temporarily unavailable</h1><p role="alert">{result.message}</p></div>;
  }
  return <div className="showcase">
    <nav className="showcase-actions"><Link href={searchHref(query)}>Back to Search</Link><form action={endSession}><button className="button">Sign out</button></form></nav>
    <ListingShowcase listing={result.data} />
    <p>Phone numbers and exact location are private.</p>
  </div>;
}
