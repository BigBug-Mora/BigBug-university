"use client";

import Link from "next/link";
import { useRef } from "react";
import type { SearchFilters } from "@/lib/search-navigation";

const areaUnits = [["perch", "Perches"], ["acre", "Acres"], ["hectare", "Hectares"],
  ["sq_m", "Square metres"], ["sq_ft", "Square feet"]];

export function SearchFiltersForm({ values }: { values: SearchFilters }) {
  const form = useRef<HTMLFormElement>(null);
  function input(name: keyof SearchFilters, title: string, numeric = false, count = false) {
    return <label key={name}>{title}<input name={name} type={numeric ? "number" : "text"}
      min={numeric ? 0 : undefined} step={numeric ? count ? "1" : "any" : undefined}
      maxLength={numeric ? undefined : name === "currency" ? 3 : 160}
      placeholder={name === "currency" ? "LKR" : undefined} defaultValue={values[name] ?? ""} /></label>;
  }
  function select(name: keyof SearchFilters, title: string, options: string[][], initial = "") {
    return <label key={name}>{title}<select name={name} defaultValue={values[name] ?? initial}>
      {options.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
    </select></label>;
  }
  return <form className="search-filters" action="/buyer/search" method="get" ref={form} aria-label="Search filters">
    <fieldset><legend>Property and location</legend>
      {select("property_type", "Property type", [["", "All property types"], ["house", "House"], ["apartment", "Apartment"], ["land", "Land"]])}
      {input("district", "District")}{input("town", "Town")}
      {select("vehicle_access", "Vehicle access", [["any", "Any"], ["required", "Required (include unknown)"],
        ["confirmed", "Confirmed only"], ["none", "No vehicle access"]], "any")}
    </fieldset>
    <fieldset><legend>Budget and rooms</legend>
      {input("currency", "Currency")}{input("min_price", "Minimum price", true)}{input("max_price", "Maximum price", true)}
      {input("min_bedrooms", "Minimum bedrooms", true, true)}{input("min_bathrooms", "Minimum bathrooms", true, true)}
    </fieldset>
    <p className="search-help">Budget bounds apply to the total asking price, including land sold per unit. A blank currency defaults to LKR when a price bound is entered.</p>
    <fieldset><legend>Minimum measurements</legend>
      {input("min_land_area", "Minimum land area", true)}{select("land_area_unit", "Land area unit", areaUnits, "perch")}
      {input("min_floor_area", "Minimum floor area", true)}{select("floor_area_unit", "Floor area unit", areaUnits.filter(([value]) => value === "sq_m" || value === "sq_ft"), "sq_m")}
    </fieldset>
    <input type="hidden" name="limit" value={values.limit ?? "20"} />
    <div className="search-actions"><button className="button button-primary" type="submit">Apply filters</button>
      <Link className="button" href="/buyer/search" onClick={() => form.current?.reset()}>Clear filters</Link>
    </div>
  </form>;
}
