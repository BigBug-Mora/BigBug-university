"use client";

import { useRouter } from "next/navigation";
import { createDraft } from "./actions";
import { actionId, Feedback, useSubmission } from "./submission";

export function Create({ account }: { account: string }) {
  const router = useRouter();
  const submit = useSubmission();
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        void submit.run(async () => {
          const type = String(data.get("type"));
          const action = await actionId(account, type);
          const result = await createDraft(action.id, type);
          if (!result.ok) return submit.setMessage(result.message);
          action.complete();
          router.push("/seller/workspace/" + result.data.listing_id);
        });
      }}
    >
      <label>
        Property type
        <select name="type">
          <option value="house">House</option>
          <option value="apartment">Apartment</option>
          <option value="land">Land</option>
        </select>
      </label>
      <button className="button button-primary" disabled={submit.busy}>
        Create draft
      </button>
      <Feedback message={submit.message} />
    </form>
  );
}
