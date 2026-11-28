import Link from "next/link";
import { pageHref } from "@/lib/search-navigation";
import { SearchResultCard } from "./result-card";
import type { SearchResults } from "./types";

export function PublishedSearchResults({ result, query }: { result: SearchResults; query: string }) {
  const { total, limit, offset, items } = result;
  const safeOffset = Number.isSafeInteger(offset);
  return <section className="search-results" aria-labelledby="search-results-title">
    <div className="search-results-heading"><h2 id="search-results-title">Search results</h2>
      <p role="status">{total} published {total === 1 ? "listing" : "listings"}{items.length ? ` · Showing ${offset + 1}–${offset + items.length}` : ""}</p></div>
    {items.length ? <div className="search-grid">{items.map((item) => <SearchResultCard key={item.listing_id} item={item} query={query} />)}</div>
      : <p className="search-empty">No published listings match these filters. Adjust a filter or clear them to search again.</p>}
    {safeOffset && (offset > 0 || offset + limit < total) && <nav className="search-actions" aria-label="Search pages">
      {offset > 0 && <Link className="button" href={pageHref(query, Math.max(0, offset - limit))} prefetch={false}>Previous page</Link>}
      {offset + limit < total && <Link className="button" href={pageHref(query, offset + limit)} prefetch={false}>Next page</Link>}
    </nav>}
  </section>;
}
