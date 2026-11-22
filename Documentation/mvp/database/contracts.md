# EstateFlow MVP database contracts

These contracts define the behavior supported by the [PostgreSQL schema](schema.md). They apply to the owning services and to any caller that retries an operation.

## Ownership and authorization

- Cognito owns credentials. The account module maps a verified Cognito issuer and subject to an EstateFlow account and stores its profile. An account can act as a buyer or seller based on its relationship to the resource.
- Property owns listings, listing revisions, facts, photo references, showcases, publications, and private value versions. Engagement owns conversations, inquiries, seller answers, and buyer-specific disclosure grants. Agent owns runs, background jobs, dispatch records, worker claims, and results.
- Derive the acting account from verified authentication. Enforce listing ownership, conversation membership, and disclosure permissions at the owning API. Resolve cross-service IDs through that API. Scope runtime database roles to service responsibilities.

## Listing revisions and publication

Every published listing requires an asking price with currency, a district, a town, and one to three distinct private phone numbers. Sellers can save incomplete drafts and must explicitly publish a specific revision and showcase.

| Property type | Required measurements and counts | Optional measurements |
| --- | --- | --- |
| House | Land area and unit, bedroom count, bathroom count | Total house floor area and unit |
| Apartment | Unit floor area and unit | Land area and unit on any floor |
| Land | Land area and unit | — |

- Land area and floor area are separate measurements. When an optional measurement is supplied, save the value and unit together. Leave optional fields `NULL` when unknown. Preserve explicit zero and false values and record the source and qualifiers of seller-supplied facts.
- The MVP supports House, Apartment, and Land. A standalone villa can use House and be described as a villa in its headline.
- A land seller can enter a total price or a price per area unit. Preserve the entered amount and unit. For budget search, convert the land area to the pricing unit and multiply by the entered price. Label the resulting total as approximate if it was calculated from an approximate land area.
- Draft edits create new revisions. Existing public listings keep their published revisions until the seller explicitly publishes an update. Commit the publication and its current pointer together. Accept only verified photos for revision attachments. Serialize changes to current phone numbers with publication and preserve at least one current phone number on a live listing.

## Ordinary seller questions and answers

- Create an inquiry after the buyer confirms the request. Group equivalent pending inquiries by listing and canonical fact key. Keep each inquiry linked to its original Property Chat.
- The seller can answer from the inbox or Seller Chat. Both use the same listing-scoped question and **Share answer** operation. Persist the exact proposed wording so it survives refresh and can be reviewed before sharing. Repeating the same action must return the same result.
- On **Share answer**, save the shared version, mark the group answered, set the current answer, and deliver that version to the original requesting chats in one Engagement transaction. Future questions in Property Chat use the current answer for that listing. A public listing update requires a separate seller action.
- When a seller shares a correction, retain both versions and move the current-answer pointer to the correction. Preserve earlier chat messages. Answer anyone who asks again using the latest shared version, including a buyer who received the previous answer.

## Private disclosures

- District and town are public. Each listing phone number, written address, and GPS pin is private. The written address and the GPS pin are independently optional. A pin contains latitude and longitude together.
- A phone request and an exact-location request are separate. For a particular buyer and listing, the seller selects which phone numbers, written address, or pin to share. A grant records each exact value version selected.
- A replacement gets a new version ID and requires fresh permission. Earlier grants cover the versions originally shared. The read path verifies the buyer, listing, and granted version before returning the protected value through its dedicated result. Chat can show status or a result reference.
- Check ownership and the selected version IDs before granting access. Commit the seller decision, the selected grants, and the request status together. Keep private values out of ordinary transcripts, model inputs, public projections, and broker messages.

## Background jobs and hosted cutover

- Accept the job and its initial dispatch record in one PostgreSQL transaction. Route dispatch and execution by the configured scope of each local stack or the hosted stack. Acknowledge broker publication in the database after confirmation and routing. A repeated publish or delivery must be safe.
- A worker claims a job with an expiring lease and renews it while working. Another worker can recover the job when the lease expires. Check the current claim when writing progress or completion. Reuse a valid result that was already saved and apply showcase results idempotently by source job ID.
- Temporary failures get three execution attempts total. Permanent failures stop immediately. After final failure, preserve the last valid draft, show the seller the reason, and offer **Try again**, which starts a new job against the current draft.
- If the seller edits the draft while a job is running, keep the edits and treat the old result as based on an earlier revision. Offer **Run on latest draft** and wait for the seller to request it.
- Before the hosted demo, stop accepting local jobs on every stack and drain local jobs and broker messages. Shut down the local stacks after verifying the drain, then run the hosted stack in its own execution scope.
