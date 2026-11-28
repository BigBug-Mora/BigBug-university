export type SearchItem = {
  listing_id: string;
  property_type: "house" | "apartment" | "land";
  district: string;
  town: string;
  headline: string;
  currency: string;
  entered_price: string;
  price_basis: "total" | "per_unit";
  price_area_unit: string | null;
  total_asking_price: string;
  total_derived_from_approximate_area: boolean | null;
  land_area: string | null;
  land_area_unit: string | null;
  land_area_approximate: boolean | null;
  floor_area: string | null;
  floor_area_unit: string | null;
  floor_area_approximate: boolean | null;
  bedroom_count: number | null;
  bathroom_count: number | null;
  vehicle_access: boolean | null;
  vehicle_access_status: "confirmed" | "false" | "unknown";
  match_status: "matched" | "needs_confirmation";
  cover_photo: null;
};

export type SearchResults = { items: SearchItem[]; total: number; limit: number; offset: number };
