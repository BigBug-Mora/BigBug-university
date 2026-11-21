# Engagement Service Container

[Container directory](containers.md) · [MVP agent behavior](../agent-details/agent-details.md)

## Runtime and owned data

Run a Python FastAPI application with SQLAlchemy and shared RDS PostgreSQL. Own buyer property conversations, transcripts, confirmed missing-fact inquiries, the grouped seller inbox, seller decisions, approved answers and their visibility, and buyer-specific disclosure requests and grants.

## Conversations and missing facts

1. Bind each Property Chat to its buyer and listing. Check access on every read or write. Save messages durably and use stable turn identifiers so retrying a submission or posting a reply does not duplicate it.
2. When the Buyer Agent identifies missing information, show an offer. Record the inquiry only after the buyer confirms. Attach equivalent confirmed inquiries to one pending property-fact group while retaining the original buyer and conversation for each.
3. Expose the grouped inbox as soon as the request is saved. A seller may leave an item pending, decline it, or approve a proposed answer with an explicit visibility decision. Check the seller's current relationship to that property through the owning boundary.
4. Store the decision, the approved fact and its provenance, and the records needed for buyer delivery consistently. Deliver an approved answer to each authorized original conversation and make it available for authorized reuse. Make repeated delivery for the same inquiry and decision safe. Status-only notices must hide the protected answer.
5. Keep the history of declined inquiries. A later confirmed equivalent inquiry can open a new pending group. A distinct fact gets a distinct group.

Enforce one pending group per property and canonical fact in the database. Handle concurrent requests and retry the operation against the group that won. The fact-matching contract must distinguish questions that sound similar but require different evidence.

## Protected disclosures

Track phone number and exact location as separate request types. A grant applies to one buyer, one listing, and one detail. A seller can leave a request pending or decline it, and an issued MVP grant remains in force. Check the grant on the dedicated result read. Keep protected values out of chat transcripts and agent context. The chat can show a status or a link to the result.

## Interactions and verification

The [Frontend](frontend.md) reads saved chats and the inbox. The [Agent API](agent-api/agent-api.md) reads authorized history and facts, persists interaction results, and uses this service for confirmations and seller decisions. The [Property service](property-service.md) owns the public listing and enforces publication independently of publishing an answer to a conversation.

Test concurrent grouping, decline and resubmission, reply deduplication, authorization for each original conversation, independent phone and location grants, and transcript retrieval after refresh. Finalize normal-answer visibility options, the reference and authorization flow for private values, and the durable delivery mechanism for approved answers and statuses.
