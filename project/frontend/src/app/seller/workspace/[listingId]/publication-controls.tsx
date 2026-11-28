"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { PreviewState } from "@/components/listing-types";
import { publishListing } from "../actions";
import { actionId, Feedback, useSubmission } from "../submission";

export function PublicationControls({ state }: { state: PreviewState }) {
  const submit = useSubmission();
  const router = useRouter();
  return <section aria-labelledby="publication-status">
    <h2 id="publication-status">Publication</h2>
    <p>{state.publication ? `Published revision ${state.publication.revision_no}. Private draft: revision ${state.revision.revision_no}.` : "This listing has not been published."}</p>
    {state.publication && <p>Published {new Date(state.publication.published_at).toLocaleString("en-LK", { timeZone: "Asia/Colombo" })}</p>}
    {!!state.missing_requirements.length ? <div><p>Before publishing:</p><ul>{state.missing_requirements.map((item) => <li key={item}>{item.replaceAll("_", " ")}</li>)}</ul></div> : <p>Ready to publish this revision and showcase.</p>}
    <div className="showcase-actions">
      <Link className="button" href={`/seller/workspace/${state.listing_id}/preview`}>Preview showcase</Link>
      <button type="button" className="button button-primary" disabled={submit.busy || !state.showcase}
        onClick={() => void submit.run(async () => {
          if (!state.showcase) return;
          const pair = { listing_revision_id: state.revision.id, showcase_id: state.showcase.id };
          const action = await actionId(state.listing_id + ":publish", pair);
          const result = await publishListing(state.listing_id, { ...pair, action_id: action.id });
          if (!result.ok) return submit.setMessage(result.message);
          action.complete();
          submit.setMessage("Listing published.");
          router.refresh();
        })}>Publish listing</button>
      {state.publication && <Link className="button" href={`/buyer/listings/${state.listing_id}`}>View published listing</Link>}
    </div>
    <Feedback message={submit.message} />
  </section>;
}
