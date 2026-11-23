# Buyer Agent

[Agent API](agent-api.md) · [Buyer Agent product behavior](../../agent-details/agent-details.md#6-buyer-agent)

## Search mode

Turn natural-language input into structured requirements and preferences, then call the [Property service](../property-service.md) search operation. Use returned published listings and their available facts to explain matches, gaps, and unknowns. For example, a plot with unknown vehicle access should remain marked as needing confirmation when the buyer requires it. Return real listing IDs for the frontend to open. The frontend restores the previous query and results when the buyer returns from Property Chat.

## Property Chat

1. Resolve the conversation, buyer, and selected listing through [Engagement service](../engagement-service.md). Scope listing tools to that listing.
2. For the MVP, pass Claude all approved facts for the selected listing that the buyer is authorized to see, using Property's buyer-visible lookup. For a dedicated field, Property returns the approved field from its shared revision or falls back to the published revision. For a flexible fact or road width, it resolves the approved fact version. Resolve the pointed-to value, source and qualifiers before building the prompt. Past messages provide conversational context. A fresh fact lookup supplies the current value. Apply the listing scope and visibility rules before building the prompt. Include the conversation messages needed to interpret the question. If the buyer asks “Is it covered?” after discussing parking, use the earlier turn to resolve the reference and the authorized facts to answer.
3. Resolve open-ended questions by meaning. Reuse the existing field or fact key when possible. For a new ordinary fact, propose its definition to Property under the [registration and sharing rules](../../database/contracts.md#ordinary-seller-questions-and-answers). Answer directly when approved evidence suffices. For a missing covered count, reuse the dedicated field and offer to ask the seller. Ask Maya only after buyer confirmation. Preserve uncertainty, units and qualifiers.
4. On confirmation, pass the inquiry to Engagement service. Equivalent pending inquiries can share one seller inbox item. Keep the original buyer and property conversation for the later answer or status.
5. Use the authorized outcome to show an approved answer, a pending status, or a decline in the original chat. A later question can reuse an approved answer within its recorded visibility. The [Seller Agent](seller-agent.md) handles the owner-facing workflow.

## Private-detail requests

Answer ordinary location questions with approved approximate information or a safe coarse result from the backend. When asked for a phone number or exact location, return the corresponding request action. The button in chat and the button on the property page invoke the same request. If the seller approves it, the chat can direct the buyer to the dedicated result. Keep the value outside model context and the chat transcript.

Verify search with unknown hard requirements, follow-up questions after refresh, changing the selected listing, an attempt to get details for a different listing, and an authorized answer reaching the original chat. Verify both private request entry points and separate results for two buyers.
