"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { PreviewState } from "@/components/listing-types";
import { label } from "@/components/listing-format";
import { saveShowcase } from "../actions";
import { actionId, Feedback, useSubmission } from "../submission";
import { PublicationControls } from "./publication-controls";

export function ShowcaseEditor({ state }: { state: PreviewState }) {
  const [headline, setHeadline] = useState(state.showcase?.headline ?? "");
  const [description, setDescription] = useState(state.showcase?.description ?? "");
  const [highlights, setHighlights] = useState(state.showcase?.highlights.join("\n") ?? "");
  const submit = useSubmission();
  const router = useRouter();
  function starter() {
    const type = label(state.revision.property_type);
    const place = [state.revision.town, state.revision.district].filter(Boolean).join(", ");
    setHeadline(`${type}${place ? ` in ${place}` : " for sale"}`);
    setDescription(`Explore this ${type.toLowerCase()}${place ? ` in ${place}` : ""}. Review the seller-stated property facts below for measurements, pricing and features.`);
    setHighlights(`${type} for sale${place ? `\nLocated in ${place}` : ""}\nSeller-stated facts available for review`);
  }
  return <>
    <section aria-labelledby="showcase-editor">
      <h2 id="showcase-editor">Showcase copy</h2>
      <p>Author the copy for saved revision {state.revision.revision_no}. Save any fact edits first, then review and publish explicitly.</p>
      {state.showcase && !state.showcase_matches_draft && <p role="status">The showcase is based on an earlier revision. Save updated copy for the current draft before publishing.</p>}
      <button className="button" type="button" onClick={starter}>Apply authored starter</button>
      <form onSubmit={(event) => {
        event.preventDefault();
        void submit.run(async () => {
          const copy = { source_revision_id: state.revision.id, parent_showcase_id: state.showcase?.id ?? null,
            headline, description, highlights: highlights.split("\n").map((text) => text.trim()).filter(Boolean) };
          const action = await actionId(state.listing_id + ":showcase", copy);
          const result = await saveShowcase(state.listing_id, { ...copy, action_id: action.id });
          if (!result.ok) return submit.setMessage(result.message);
          action.complete();
          submit.setMessage("Showcase saved.");
          router.refresh();
        });
      }}>
        <label>Headline<input name="headline" required maxLength={240} value={headline} onChange={(e) => setHeadline(e.target.value)} /></label>
        <label>Description<textarea name="description" required maxLength={5000} rows={5} value={description} onChange={(e) => setDescription(e.target.value)} /></label>
        <label>Highlights (one per line)<textarea name="highlights" required rows={4} value={highlights} onChange={(e) => setHighlights(e.target.value)} /></label>
        <button className="button" disabled={submit.busy}>Save showcase</button>
        <Feedback message={submit.message} />
      </form>
    </section>
    <PublicationControls state={state} />
  </>;
}
