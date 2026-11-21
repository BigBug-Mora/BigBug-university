# Buyer Agent

[Agent API](agent-api.md) · [Buyer Agent product behavior](../../agent-details/agent-details.md#6-buyer-agent)

## Search mode

Turn natural-language input into structured requirements and preferences, then call the [Property service](../property-service.md) search operation. Use returned published listings and their available facts to explain matches, gaps, and unknowns. For example, a plot with unknown vehicle access should remain marked as needing confirmation when the buyer requires it. Return real listing IDs for the frontend to open. The frontend restores the previous query and results when the buyer returns from Property Chat.

## Property Chat

1. Resolve the conversation, buyer, and selected listing through [Engagement service](../engagement-service.md). Scope listing tools to that listing.
2. Load relevant conversation messages, published listing facts, and approved answers visible to that buyer. If the buyer asks “Is it covered?” after discussing parking, use the earlier turn to resolve the reference while grounding the answer in the listing and authorized facts.
3. Preserve the source and qualifiers of each claim. If covered parking is unknown, explain what remains unknown and offer the buyer a confirmation action to ask the seller.
4. On confirmation, pass the inquiry to Engagement service. Equivalent pending inquiries can share one seller inbox item. Keep the original buyer and property conversation for the later answer or status.
5. Use the authorized outcome to show an approved answer, a pending status, or a decline in the original chat. A later question can reuse an approved answer within its recorded visibility. The [Seller Agent](seller-agent.md) handles the owner-facing workflow.

## Private-detail requests

Answer ordinary location questions with approved approximate information or a safe coarse result from the backend. When asked for a phone number or exact location, return the corresponding request action. The button in chat and the button on the property page invoke the same request. If the seller approves it, the chat can direct the buyer to the dedicated result. Keep the value outside model context and the chat transcript.

Verify search with unknown hard requirements, follow-up questions after refresh, changing the selected listing, an attempt to get details for a different listing, and an authorized answer reaching the original chat. Verify both private request entry points and separate results for two buyers.
