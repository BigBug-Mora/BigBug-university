"use server";

import { propertyRequest } from "@/server/property";

const id = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;
const invalid = { ok: false as const, status: 422, message: "Invalid listing or detail identifier." };

export async function createDraft(action: string, type: string) {
  return propertyRequest<{listing_id: string}>("", "POST", {create_action_id: action, draft: {property_type: type}});
}

export async function saveDraft(listing: string, parent: string, action: string, draft: Record<string, unknown>) {
  if (!id.test(listing)) return invalid;
  return propertyRequest<{revision: {id: string; revision_no: number}}>(`/${listing}/revisions`, "POST",
    {parent_revision_id: parent, edit_action_id: action, draft});
}

export async function updateDetail(listing: string, kind: string, slot: number, value: unknown) {
  if (!id.test(listing) || !["phone","written_address","map_pin"].includes(kind) || !Number.isInteger(slot)) return invalid;
  return propertyRequest<{id: string}>(`/${listing}/private-details/${kind}/${slot}`, "PUT", {value});
}

export async function removeDetail(listing: string, detail: string) {
  if (!id.test(listing) || !id.test(detail)) return invalid;
  return propertyRequest<null>(`/${listing}/private-details/${detail}`, "DELETE");
}
