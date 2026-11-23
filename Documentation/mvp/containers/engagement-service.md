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

Track phone number and exact location as separate request types. A seller can grant access to selected phone numbers, the written address, or the map pin for the requesting buyer and listing. Store one grant per selected detail ID. Verify each selection through Property service before granting access. A seller can also leave the request pending or decline it.

On every protected result read, verify the buyer and resolve only the granted detail IDs through Property service. Return the current value of each active detail. Show retired details as unavailable. The chat can show status or a link to the result, and protected values stay in the dedicated result.

## Interactions and verification

The [Frontend](frontend.md) reads saved chats and the inbox. The [Agent API](agent-api/agent-api.md) reads authorized history and facts, persists interaction results, and uses this service for confirmations and seller decisions. The [Property service](property-service.md) owns the public listing and enforces publication independently of publishing an answer to a conversation.

Test concurrent grouping, decline and resubmission, reply deduplication, authorization for each original conversation, independent phone and location grants, edits to shared details, retirement and reuse of a slot, and transcript retrieval after refresh. Finalize normal-answer visibility options and the durable delivery mechanism for approved answers and statuses.
