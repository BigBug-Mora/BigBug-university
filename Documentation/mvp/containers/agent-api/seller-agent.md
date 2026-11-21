# Seller Agent

[Agent API](agent-api.md) · [Seller Agent product behavior](../../agent-details/agent-details.md#3-seller-agent)

## Listing preparation and specialist handoffs

Load the authorized seller draft from [Property service](../property-service.md). Extract structured proposals from seller input, keep unanswered fields unknown, and retain source and uncertainty. Ask for type-specific details where helpful. Submit seller-confirmed edits through the property boundary.

Request a [Property Inspector](../agent-worker/property-inspector-agent.md) job for the current draft and photos. Present the findings as an optional checklist. For example, suggest a clearer entrance photo or a missing kitchen photo without making it a condition for publishing. Request a [Property Showcase Creator](../agent-worker/property-showcase-creator-agent.md) job with the approved publishable facts and relevant findings. Show the editable result and offer the separate owner review and publication action. Publication belongs to Property service.

## Seller inbox

1. Use [Engagement service](../engagement-service.md) to show the current grouped summary. Preserve property and inquiry scope. Each group can include several buyers who asked about the same underlying fact.
2. Interpret the seller's response as a proposed answer. Preserve qualifiers and ask for clarification when a response is ambiguous. For example, confirm whether an approximate width refers to the access road or the main road.
3. Show the proposed answer and visibility to the seller for explicit confirmation. The seller may answer, decline, or leave an item pending. Pass an authorized decision to Engagement service for durable storage and delivery to the original chats.
4. Handle phone and exact-location requests as separate grant decisions. Surface the request type and buyer. The protected result is handled by the backend after explicit approval.

## Verification

Check that suggested edits preserve unknowns and qualifiers, ignored photo suggestions leave the seller free to publish when requirements are met, and a public revision requires its own approval. Verify that an unapproved answer stays pending, restricted answers reach only authorized buyers, and one disclosure decision leaves the other detail protected.
