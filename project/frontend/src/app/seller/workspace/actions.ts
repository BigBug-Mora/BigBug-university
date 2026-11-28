"use server";

import { propertyRequest } from "@/server/property";
import { revalidatePath } from "next/cache";

const id = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;
const invalid = {
  ok: false as const,
  status: 422,
  message: "Invalid listing or detail identifier.",
};

export async function createDraft(action: string, type: string) {
  const result = await propertyRequest<{ listing_id: string }>("", "POST", {
    create_action_id: action,
    draft: { property_type: type },
  });
  if (result.ok) revalidatePath("/seller/workspace");
  return result;
}

export async function saveDraft(
  listing: string,
  parent: string,
  action: string,
  draft: Record<string, unknown>,
) {
  if (!id.test(listing)) return invalid;
  return propertyRequest<{ revision: { id: string; revision_no: number } }>(
    `/${listing}/revisions`,
    "POST",
    { parent_revision_id: parent, edit_action_id: action, draft },
  );
}

export async function updateDetail(
  listing: string,
  kind: string,
  slot: number,
  value: unknown,
) {
  if (
    !id.test(listing) ||
    !["phone", "written_address", "map_pin"].includes(kind) ||
    !Number.isInteger(slot)
  )
    return invalid;
  return propertyRequest<{ id: string }>(
    `/${listing}/private-details/${kind}/${slot}`,
    "PUT",
    { value },
  );
}

export async function removeDetail(listing: string, detail: string) {
  if (!id.test(listing) || !id.test(detail)) return invalid;
  return propertyRequest<null>(
    `/${listing}/private-details/${detail}`,
    "DELETE",
    undefined,
    true,
  );
}

export async function saveShowcase(
  listing: string,
  payload: {
    action_id: string;
    source_revision_id: string;
    parent_showcase_id?: string | null;
    headline: string;
    description: string;
    highlights: string[];
  },
) {
  if (!id.test(listing) || !id.test(payload.source_revision_id)) return invalid;
  const result = await propertyRequest<Record<string, unknown>>(
    `/${listing}/showcases`,
    "POST",
    payload,
    true,
  );
  if (result.ok) {
    revalidatePath(`/seller/workspace/${listing}`);
    revalidatePath(`/seller/workspace/${listing}/preview`);
  }
  return result;
}

export async function publishListing(
  listing: string,
  payload: {
    action_id: string;
    listing_revision_id: string;
    showcase_id: string;
  },
) {
  if (
    !id.test(listing) ||
    !id.test(payload.listing_revision_id) ||
    !id.test(payload.showcase_id)
  )
    return invalid;
  const result = await propertyRequest<{
    publication_id: string;
    listing_id: string;
    listing_revision_id: string;
    revision_no: number;
    showcase_id: string;
    published_at: string;
  }>(`/${listing}/publish`, "POST", payload, true);
  if (result.ok) {
    revalidatePath("/seller/workspace");
    revalidatePath(`/seller/workspace/${listing}`);
    revalidatePath(`/seller/workspace/${listing}/preview`);
    revalidatePath(`/buyer/listings/${listing}`);
  }
  return result;
}
