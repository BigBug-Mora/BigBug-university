import Image from "next/image";
import { label, measurement, money, previewTotal, scalar } from "./listing-format";
import type { ListingView } from "./listing-types";

const common = ["parking_spaces", "covered_parking_spaces", "vehicle_access", "construction_status",
  "has_mains_water", "has_well_water", "has_electricity", "has_garden", "has_boundary_wall", "price_negotiable"];
const building = ["bedroom_count", "bathroom_count", "attached_bathroom_count", "separate_toilet_count",
  "ground_floor_bedrooms", "year_built", "furnishing_status"];

export function ListingShowcase({ listing }: { listing: ListingView }) {
  const gallery = listing.gallery_photos;
  const cover = gallery[0];
  const features = listing.featured_photos.slice(0, 3);
  const perUnit = listing.price_basis === "per_unit";
  const total = listing.total_asking_price ?? previewTotal(listing);
  const approximate = listing.total_derived_from_approximate_area ?? (perUnit && listing.land_area_approximate);
  const fields = [...common, ...(listing.property_type === "land" ? [] : building),
    ...(listing.property_type === "house" ? ["house_storey_count"] : []),
    ...(listing.property_type === "apartment" ? ["apartment_floor_no"] : [])];
  const metrics = [
    ["Land area", measurement(listing.land_area, listing.land_area_unit, listing.land_area_approximate)],
    ...(listing.property_type === "land" ? [] : [
      ["Floor area", measurement(listing.floor_area, listing.floor_area_unit, listing.floor_area_approximate)],
      ["Bedrooms", scalar(listing.bedroom_count)], ["Bathrooms", scalar(listing.bathroom_count)],
    ]),
  ];
  const evidence = listing.standard_fact_evidence as Record<string, { qualifier?: string; source_kind?: string }> | undefined;
  return (
    <article className="showcase">
      <header className="showcase-hero">
        <p className="showcase-eyebrow">{label(listing.property_type)} · {scalar(listing.town)} · {scalar(listing.district)}</p>
        <h1>{listing.headline}</h1>
        <div className="showcase-price" data-testid="asking-price">
          {money(listing.entered_price, listing.currency)}{perUnit && ` / ${scalar(listing.price_area_unit).replaceAll("_", " ")}`}
          {perUnit && <p>{approximate === true ? "Approximate total" : "Total asking price"}: {money(total, listing.currency)}</p>}
        </div>
        {!gallery.length && <p className="showcase-photo-note">No photos published yet</p>}
      </header>
      {cover?.url && <Image className="showcase-cover" src={cover.url} alt={cover.caption || listing.headline} width={1200} height={800} unoptimized />}
      <dl className="showcase-stats">
        {metrics.map(([name, value]) => <div key={name}><dt className="showcase-stat-label">{name}</dt><dd className="showcase-stat-value">{value}</dd></div>)}
      </dl>
      <section className="showcase-section" aria-labelledby="highlights">
        <h2 id="highlights">At a glance</h2>
        <ul className="showcase-highlights">{listing.highlights.map((text, i) => <li key={i}>{text}</li>)}</ul>
      </section>
      <section className="showcase-section" aria-labelledby="description">
        <h2 id="description">A closer look</h2>
        <p className="showcase-description">{listing.description}</p>
      </section>
      {!!gallery.length && !!features.length && <section className="showcase-section showcase-story" aria-label="Photo story">
        {features.map((photo) => <div key={photo.photo_id} className="showcase-story-row">
          {photo.url && <Image src={photo.url} alt={photo.title || "Property detail"} width={800} height={600} unoptimized />}
          <div><h2>{photo.title}</h2><p>{photo.body}</p></div>
        </div>)}
      </section>}
      <section className="showcase-section" aria-labelledby="property-facts">
        <h2 id="property-facts">Property facts</h2>
        <p>Seller-stated information. Unknown values need confirmation; measurements marked approximate are estimates.</p>
        <dl className="showcase-facts">
          {fields.map((key) => <div className="showcase-fact-row" key={key}>
            <dt className="showcase-fact-key">{label(key)}</dt>
            <dd className="showcase-fact-val">{typeof listing[key] === "string" && /status$/.test(key) ? label(String(listing[key])) : scalar(listing[key])}
              {evidence?.[key]?.qualifier && <small>{evidence[key].qualifier}</small>}
            </dd>
          </div>)}
          {listing.facts.map((fact) => <div className="showcase-fact-row" key={fact.fact_key}>
            <dt className="showcase-fact-key">{fact.display_name || label(fact.fact_key)}</dt>
            <dd className="showcase-fact-val">
              {fact.evidence_state && fact.evidence_state !== "known" ? label(fact.evidence_state) :
                fact.value_kind === "number" ? measurement(fact.number_value, fact.unit || "", fact.approximate) :
                  scalar(fact.value_kind === "boolean" ? fact.boolean_value : fact.text_value)}
              <small>{fact.source_kind === "seller" ? "Seller-stated" : "Source recorded"}{fact.qualifier ? ` · ${fact.qualifier}` : ""}</small>
            </dd>
          </div>)}
        </dl>
      </section>
      {!!gallery.length && <section className="showcase-section" aria-labelledby="gallery">
        <h2 id="gallery">Gallery</h2><div className="showcase-gallery">
          {gallery.map((photo) => <figure key={photo.photo_id}>
            {photo.url && <Image src={photo.url} alt={photo.caption || "Property photo"} width={800} height={600} unoptimized />}
            {photo.caption && <figcaption>{photo.caption}</figcaption>}
          </figure>)}
        </div>
      </section>}
    </article>
  );
}
