import Link from "next/link";
import { listingSearchHref } from "@/lib/search-navigation";
import { label, measurement, money, scalar } from "@/components/listing-format";
import type { SearchItem } from "./types";

const accessLabels = { confirmed: "Confirmed", false: "No vehicle access", unknown: "Unknown — needs confirmation" };

export function SearchResultCard({ item, query }: { item: SearchItem; query: string }) {
  const perUnit = item.price_basis === "per_unit";
  const metrics = [["Land area", measurement(item.land_area, item.land_area_unit, item.land_area_approximate)],
    ...(item.property_type === "land" ? [] : [
      ["Floor area", measurement(item.floor_area, item.floor_area_unit, item.floor_area_approximate)],
      ["Bedrooms", scalar(item.bedroom_count)], ["Bathrooms", scalar(item.bathroom_count)],
    ])];
  return <article className="search-card" data-testid="search-card" data-listing-id={item.listing_id}>
    <div className="search-card-header"><span className="showcase-eyebrow">{label(item.property_type)}</span><span>No photos published yet</span></div>
    <div className="search-card-body">
      <p className="search-location">{item.town}, {item.district}</p>
      <h3><Link href={listingSearchHref(item.listing_id, query)} prefetch={false}>{item.headline}</Link></h3>
      <p className="search-price">{money(item.entered_price, item.currency)}{perUnit ? ` / ${item.price_area_unit?.replaceAll("_", " ")}` : ""}</p>
      {perUnit && <p className="search-total">{item.total_derived_from_approximate_area === true ? "Approximate total" : "Total asking price"}: {money(item.total_asking_price, item.currency)}</p>}
      <p className="search-access" data-access={item.vehicle_access_status}><span>Vehicle access: </span>{accessLabels[item.vehicle_access_status]}</p>
      <dl className="search-metrics">{metrics.map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl>
    </div>
  </article>;
}
