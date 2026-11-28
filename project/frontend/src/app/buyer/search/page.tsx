import { redirect } from "next/navigation";
import { endSession } from "@/app/actions";
import { SearchFiltersForm } from "@/components/search/filters";
import { PublishedSearchResults } from "@/components/search/results";
import { searchHref, searchState } from "@/lib/search-navigation";
import { searchPublishedListings } from "@/server/property";
import { protectedAccount } from "@/server/session";

export default async function SearchPage({ searchParams }: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const state = searchState(await searchParams);
  const destination = searchHref(state.query);
  const actor = await protectedAccount(destination);
  if (actor.status !== "active") return <h1>{actor.status === "forbidden" ? "Access denied" : "Service temporarily unavailable"}</h1>;
  const standalone = process.env.ESTATEFLOW_TEST_STANDALONE_FIXTURES === "1"
    && process.env.ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER === "1";
  const result = state.valid && !standalone ? await searchPublishedListings(state.request) : null;
  if (result && !result.ok && result.status === 401) redirect(`/sign-in?returnTo=${encodeURIComponent(destination)}&status=expired`);
  if (result && !result.ok && result.status === 403) return <h1>Access denied</h1>;
  return <div className="buyer-search">
    <header className="search-page-heading"><div><h1>Buyer search</h1><p>Find a property in the details that matter.</p></div>
      <form action={endSession}><button className="button">Sign out</button></form></header>
    <p className="search-account">Account <span className="break-all font-mono">{actor.accountId}</span></p>
    <SearchFiltersForm key={state.query} values={state.filters} />
    {!state.valid && <p role="alert">The search URL contains unsupported or repeated filters. Clear filters and try again.</p>}
    {standalone && <p>Search results are unavailable in the standalone sign-in fixture.</p>}
    {result && (!result.ok ? <p role="alert">{result.status === 422
      ? "Check the price range, currency, minimum measurements and units, counts, and page settings."
      : result.message}</p> : <PublishedSearchResults result={result.data} query={state.query} />)}
  </div>;
}
