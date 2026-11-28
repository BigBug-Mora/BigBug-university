export type PublicFact = {
  fact_key: string;
  display_name?: string;
  value_kind: string;
  evidence_state?: string;
  number_value?: string | null;
  boolean_value?: boolean | null;
  text_value?: string | null;
  unit?: string | null;
  approximate?: boolean | null;
  qualifier?: string | null;
  source_kind?: string;
  approved_for_public?: boolean;
};

export type ShowcaseCopy = {
  id: string;
  source_revision_id: string;
  headline: string;
  description: string;
  highlights: string[];
};

export type Photo = {
  photo_id: string;
  url?: string;
  caption?: string | null;
  title?: string;
  body?: string;
};

export type ListingView = Record<string, unknown> & {
  listing_id: string;
  property_type: string;
  headline: string;
  description: string;
  highlights: string[];
  facts: PublicFact[];
  gallery_photos: Photo[];
  featured_photos: Photo[];
};

export type PreviewState = {
  listing_id: string;
  revision: Record<string, unknown> & { id: string; property_type: string; revision_no: number };
  facts: PublicFact[];
  showcase: ShowcaseCopy | null;
  showcase_matches_draft: boolean;
  missing_requirements: string[];
  publication: { revision_no: number; published_at: string } | null;
};

export function previewView(state: PreviewState): ListingView | null {
  if (!state.showcase || !state.showcase_matches_draft) return null;
  return {
    ...state.revision,
    listing_id: state.listing_id,
    property_type: state.revision.property_type,
    headline: state.showcase.headline,
    description: state.showcase.description,
    highlights: state.showcase.highlights,
    facts: state.facts.filter((fact) => fact.approved_for_public),
    gallery_photos: [],
    featured_photos: [],
  };
}
