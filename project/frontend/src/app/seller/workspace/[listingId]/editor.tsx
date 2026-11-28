"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { saveDraft } from "../actions";
import { actionId, Feedback, useSubmission } from "../submission";

type Scalar = string | boolean | number | null;
export type Revision = {
  id: string;
  revision_no: number;
  property_type: string;
  standard_fact_evidence: Record<string, unknown>;
} & Record<string, unknown>;
export type Width = {
  approved_for_public?: boolean;
  number_value: string;
  unit: string;
  approximate: boolean | null;
  qualifier: string | null;
};
const units = ["sq_m", "sq_ft", "perch", "acre", "hectare"];
const booleanFields = [
  "price_negotiable",
  "vehicle_access",
  "has_mains_water",
  "has_well_water",
  "has_electricity",
  "has_garden",
  "has_boundary_wall",
];
const buildingCounts = [
  "bedroom_count",
  "bathroom_count",
  "attached_bathroom_count",
  "separate_toilet_count",
  "ground_floor_bedrooms",
  "year_built",
];
function label(key: string) {
  if (key === "road_number_value") return "Access road width";
  return key[0].toUpperCase() + key.slice(1).replaceAll("_", " ");
}

export function Editor({
  listing,
  revision,
  width,
}: {
  listing: string;
  revision: Revision;
  width?: Width;
}) {
  const type = revision.property_type;
  const counts = [
    "parking_spaces",
    "covered_parking_spaces",
    ...(type === "land" ? [] : buildingCounts),
    ...(type === "house"
      ? ["house_storey_count"]
      : type === "apartment"
        ? ["apartment_floor_no"]
        : []),
  ];
  const [parent, setParent] = useState(revision.id);
  const [number, setNumber] = useState(revision.revision_no);
  const [basis, setBasis] = useState(String(revision.price_basis ?? ""));
  const submit = useSubmission();
  const router = useRouter();
  function field(
    key: string,
    options?: string[],
    numeric = false,
    initial: unknown = revision[key],
  ) {
    return (
      <label key={key}>
        {label(key)}
        {options ? (
          <select
            name={key}
            defaultValue={String(initial ?? "")}
            onChange={
              key === "price_basis"
                ? (e) => setBasis(e.target.value)
                : undefined
            }
          >
            <option value="">Unknown</option>
            {options.map((v) => (
              <option key={v} value={v}>
                {v === "true" ? "Yes" : v === "false" ? "No" : label(v)}
              </option>
            ))}
          </select>
        ) : (
          <input
            name={key}
            type={numeric ? "number" : "text"}
            step={counts.includes(key) ? "1" : "any"}
            placeholder="Unknown"
            defaultValue={String(initial ?? "")}
          />
        )}
      </label>
    );
  }
  const tri = ["true", "false"];
  return (
    <section>
      <h2>Listing facts</h2>
      <p>Revision {number}. Leave an unknown value blank.</p>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          void submit.run(async () => {
            const fields: Record<string, unknown> = {
              property_type: type,
              standard_fact_evidence: revision.standard_fact_evidence,
              access_road_width_approved_for_public: data.has("access_road_width_approved_for_public"),
            };
            const road: Record<string, Scalar> = {};
            for (const [key, raw] of data) {
              if (key === "access_road_width_approved_for_public") continue;
              const text = String(raw).trim();
              let value: Scalar = text || null;
              if (text && counts.includes(key)) value = Number(text);
              if (
                text &&
                (booleanFields.includes(key) || key.endsWith("_approximate"))
              )
                value = text === "true";
              if (key.startsWith("road_")) road[key.slice(5)] = value;
              else fields[key] = value;
            }
            fields.access_road_width = Object.values(road).every(
              (v) => v === null,
            )
              ? null
              : road;
            const action = await actionId(listing, [parent, fields]);
            const result = await saveDraft(listing, parent, action.id, fields);
            if (!result.ok) return submit.setMessage(result.message);
            action.complete();
            setParent(result.data.revision.id);
            setNumber(result.data.revision.revision_no);
            submit.setMessage("Draft saved.");
            router.refresh();
          });
        }}
      >
        <fieldset>
          <legend>Location and price</legend>
          {field("district")}
          {field("town")}
          {field(
            "price_basis",
            type === "land" ? ["total", "per_unit"] : ["total"],
          )}
          {basis && (
            <>
              {field("entered_price", undefined, true)}
              {field("currency")}
            </>
          )}
          {basis === "per_unit" && field("price_area_unit", units)}
          {field("price_negotiable", tri)}
        </fieldset>
        <fieldset>
          <legend>Measurements</legend>
          {field("land_area", undefined, true)}
          {field("land_area_unit", units)}
          {field("land_area_approximate", tri)}
          {type !== "land" && (
            <>
              {field("floor_area", undefined, true)}
              {field("floor_area_unit", units.slice(0, 2))}
              {field("floor_area_approximate", tri)}
            </>
          )}
          {field("road_number_value", undefined, true, width?.number_value)}
          {field("road_unit", ["ft", "m"], false, width?.unit)}
          {field("road_approximate", tri, false, width?.approximate)}
          {field("road_qualifier", undefined, false, width?.qualifier)}
          <label className="checkbox-label"><input name="access_road_width_approved_for_public" type="checkbox" defaultChecked={width?.approved_for_public ?? false} />Show access road width on the published page</label>
        </fieldset>
        <fieldset>
          <legend>Property features</legend>
          {counts.map((k) => field(k, undefined, true))}
          {field("construction_status", [
            "planned",
            "under_construction",
            "completed",
          ])}
          {type !== "land" &&
            field("furnishing_status", [
              "unfurnished",
              "partly_furnished",
              "furnished",
            ])}
          {booleanFields.slice(1).map((k) => field(k, tri))}
        </fieldset>
        <button className="button button-primary" disabled={submit.busy}>
          Save draft
        </button>
        <Feedback message={submit.message} />
      </form>
    </section>
  );
}
