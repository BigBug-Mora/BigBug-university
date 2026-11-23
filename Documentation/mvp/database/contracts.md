# EstateFlow MVP database contracts

These contracts define the behavior supported by the [PostgreSQL schema](schema.md). They apply to the owning services and to any caller that retries an operation.

## Ownership and authorization

- Cognito owns credentials. The account module maps a verified Cognito issuer and subject to an EstateFlow account and stores its profile. An account can act as a buyer or seller based on its relationship to the resource.
- Property owns listings, listing revisions, facts, photo references, showcases, publications, and current private details. Engagement owns conversations, inquiries, seller answers, and buyer-specific disclosure grants. Agent owns runs, background jobs, dispatch records, worker claims, and results.
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
- Draft edits create new revisions. Existing public listings keep their published revisions until the seller explicitly publishes an update. Commit the publication and its current pointer together. Accept only verified photos for revision attachments. Serialize changes to phone details with publication, keep active numbers distinct, and preserve at least one active phone number on a live listing.

## Standard fields and flexible facts

- Road width and flexible facts use immutable fact versions. Price, location, measurements, counts and other dedicated fields live on `property.listing_revisions`. Covered parking uses the existing count column and its SQL checks against zero and total parking. Keep its source and qualifiers in that revision's `standard_fact_evidence`. Private details use buyer-specific disclosure.
- Property maintains an allowlist mapping each supported dedicated inquiry key to a typed field reader, writer, and evidence entry. Register it with `storage_kind = 'dedicated'` and its applicability. Covered parking and bedroom count are the initial mappings. Reserve all dedicated field names and meanings when resolving new questions. Extending sharing to another dedicated field requires its mapping, including units and qualifiers where applicable. Only trusted application code selects columns.
- For land area, floor area, and access-road width, record the seller's stated precision. Use `true` for an estimate, `false` for a value the seller explicitly supplies as a measurement, and `NULL` when the seller leaves precision unspecified. Leave the value, unit, and flag `NULL` when the measurement is missing. If precision matters and the seller's wording is unclear, ask them. A seller-reported measurement retains its attribution.
- Register each versioned key and its value type in `property.fact_definitions` and its eligible property types in `property.fact_applicability` before accepting inquiries. Property checks applicability. One immutable `property.fact_versions` row stores one listing's value, unit, precision and source for that key. Allocate its version number under the listing lock. A new version may exist privately while a seller reviews a proposal. Known values match their declared type. Unknown and disputed versions carry no confirmed value.
- Each saved revision freezes its fact links and their page approvals in `property.revision_facts`. A change to which facts appear on the page creates a new draft revision, even when all values are identical. Copy the other links, approvals and photo attachments. Bind each approval to the exact fact version reviewed. Preview the showcase for that revision, then publish the matching pair. The Publish transaction reads the frozen selection. For example, hiding road width while editing a live listing affects the public page only when Maya publishes the new revision.
- **Save draft** advances `listings.current_draft_revision_id`. **Save and generate showcase** first saves the edits and submits a job for that exact revision. A failed generation leaves the saved draft available. After a change, suggest **Regenerate showcase** in the editor. Publication pairs a revision only with a showcase generated from it.

## Which value a buyer sees

For a versioned fact, follow the buyer-visible pointer to its fact version. For a dedicated key, read the mapped column and its evidence from `field_revision_id` if shared, otherwise from the live publication's revision. Authorize the listing first and project only the requested field and associated evidence. A missing, unknown or disputed answer leads to the missing-information flow. The public page reads the live publication's dedicated fields and frozen public-approved fact links.

For versioned keys, bind the listing ID to `$1` and the key to `$2`.

```sql
SELECT f.value_kind, f.evidence_state, f.number_value, f.boolean_value,
       f.text_value, f.unit, f.approximate, f.source_kind, f.qualifier, f.certainty
FROM property.buyer_visible_facts AS b
JOIN property.fact_versions AS f ON f.id = b.fact_version_id
WHERE b.listing_id = $1 AND b.fact_key = $2;
```

- **Save draft** changes only the editor's revision. **Share answer** sets the buyer-visible pointer for the one approved key.
- For dedicated fields, Publish compares each mapped value and its evidence across the outgoing and incoming publications. A changed published value takes effect by clearing its chat override in the same transaction. A newly published known value also supersedes its override. An unrelated edit preserves the override. Clearing a published value removes the override only if it refers to that outgoing value and evidence; preserve an independently shared correction. Reads then follow the pointer or published fallback described above.
- **Publish** locks the listing and compares the public-approved fact links on the outgoing and incoming published revisions. Insert or update pointers for newly public or changed versions. On the first publication, insert the public-approved facts. For a removed public fact, delete its pointer if it still points to the removed version. Preserve independently shared answers to other versions. Leave all other keys alone, including chat-only keys. Commit these changes with the publication and current-publication pointer. A replay returns the original result.
- Maya publishes road width at 15 ft, shares 14 ft, and privately saves 13 ft. The page shows 15 ft, Property Chat answers 14 ft, and the editor opens at 13 ft. Publishing the 13-foot revision and its matching showcase changes both buyer reads to 13 ft. An earlier message delivering 14 ft retains its wording.

## Showcase photos

- `revision_photos` records which verified photos belong to the source listing revision and their draft order. `showcase_photos` records the full gallery for one showcase, its display order, and optional captions. Use the first photo in gallery order as the cover.
- `showcase_featured_photos` records up to three distinct gallery photos in a separate story order. Each feature has a title and a one- or two-sentence write-up grounded in the photo or approved property facts. Featured photos also appear in the full gallery at the bottom of the detail page.
- Save the showcase revision, gallery, and featured story together. The database checks that featured photos belong to that showcase's gallery. Property service validates the text and returns the gallery and featured story from the exact published showcase. Fewer usable photos may produce fewer featured write-ups.

## Ordinary seller questions and answers

- Buyers ask in their own words. Resolve the underlying question against existing listing fields and the fact catalog, then answer from authorized evidence when sufficient. A known covered count of two answers both “Is parking covered?” and “How many covered spaces are there?” A seller's bare “yes” establishes presence only. Ask for the count before recording a number.
- For a genuinely new ordinary fact, the agent proposes a precise definition, a supported value kind (number, boolean or text), applicable property types and a unit when appropriate. Property checks for equivalent meanings and existing dedicated fields before registering a key. It saves the definition and applicability together. On a concurrent registration of the same key, reuse it after checking its meaning and type. Clarify ambiguous questions and preserve material distinctions such as entering a gate versus turning inside it. Route private details through disclosure.
- Registration describes a question across listings. Only seller-approved evidence supplies its shared answer for this listing. For example, “Can a large truck turn inside the gate?” can introduce a boolean key. A later equivalent question can reuse Maya's confirmed answer and qualifiers. If her reply describes a different vehicle or leaves the answer uncertain, clarify before sharing. Dedicated fields retain their existing meaning. When a reply establishes one, use its typed Property mapping for sharing. A key that lacks a dedicated write mapping requires one before a structured share can complete.

- Create an inquiry after the buyer confirms the request. Group equivalent pending inquiries by listing and canonical fact key. Keep each inquiry linked to its original Property Chat.
- The seller can answer from the inbox or Seller Chat. Both use the same listing-scoped question and **Share answer** operation. Persist the exact proposed wording so it survives refresh and can be reviewed before sharing. Repeating the same action must return the same result.
- A proposal stores its wording and reviewed draft revision. For a versioned key it references the proposed fact version. For a dedicated key it stages the proposed scalar in `proposed_field_value`; Property validates it against the mapped column and captures the reviewed qualifiers with the wording. Preparing a proposal grants no buyer access.
- **Share answer** is one seller action and one PostgreSQL transaction. Engagement coordinates a narrow Property-owned database operation on the same connection to validate ownership, lock the listing and apply the fact. Check for a completed replay under the lock first. For a versioned key compare the reviewed draft's link with the latest draft's link. Preserve unrelated edits. If this key changed to a different version in the meantime, show the conflict for review before committing. If the latest draft already uses the proposed version, reuse the revision. Otherwise save a new revision from the latest draft, replacing only this key and advancing the editor pointer.
- In that transaction set the buyer-visible pointer, insert the shared answer with its stable share action ID, and move `engagement.current_answers` to the approved chat wording. For a pending group also record its resolution, mark it answered and deliver to its original chats. Roll back all writes on failure. A replay returns the original outcome without moving later pointers. Limit the coordinating role to the required Property operation and Engagement writes.
- For a dedicated key compare the reviewed field and its evidence with the latest draft. Apply just the approved field and evidence through its typed setter, preserving other edits and enforcing revision constraints. For both storage paths record the resulting `shared_answers.applied_revision_id`. For dedicated keys the approval identifies the value by that revision and its `fact_key`; set the chat pointer's `field_revision_id` to that revision. For versioned keys the approved proposal and the pointer use the same `fact_version_id`. Reuse the current draft if its value and evidence already match.
- Example: the published covered count is unknown, and the editor already contains a private price change. Maya shares “two covered spaces.” The parking lookup can now return two from the applied revision. A price lookup still uses the published price. Earlier chat deliveries resolve their original approval.
- A correction can originate in Seller Chat without a pending group. Use the same operation, link the superseded answer and retain the original deliveries. Declining a request records its resolution and status delivery without a fact update. Sharing an ordinary answer makes that fact available for future questions about the listing. Only explicit publication changes the public page.

## Private disclosures

- District and town are public. Each listing phone number, written address, and GPS pin is private. The written address and the GPS pin are independently optional. A pin contains latitude and longitude together.
- Phone and exact-location requests are separate. The seller can share one or more selected phone numbers, or the written address, map pin, or both, with the requesting buyer. Each grant records the selected detail's stable ID.
- Property keeps one current encrypted value per detail. Editing a phone number, address, or pin updates that value in place. Buyers who already have access see the updated value the next time they open the protected result. Edits to private details take effect independently of listing publication.
- Removing a detail clears its value and retires its ID permanently. Keep the retired record and existing grants as history. A buyer's result shows a removed detail as unavailable. A detail added later in the same slot gets a new ID and requires its own grant. A detail ID stays bound to its original listing and kind.
- Check seller ownership and each selected detail's listing, kind, and active state before granting access. Commit the seller decision, the selected grants, and the request status together. On each protected read, check the signed-in buyer and grant, then resolve only the granted IDs against that listing and kind. Chat can show status or a result reference. Keep private values out of ordinary transcripts, model inputs, public projections, and broker messages.

## Background jobs and hosted cutover

- Accept the job and its initial dispatch record in one PostgreSQL transaction. Route dispatch and execution by the configured scope of each local stack or the hosted stack. Acknowledge broker publication in the database after confirmation and routing. A repeated publish or delivery must be safe.
- A worker claims a job with an expiring lease and renews it while working. Another worker can recover the job when the lease expires. Check the current claim when writing progress or completion. Reuse a valid result that was already saved and apply showcase results idempotently by source job ID.
- Temporary failures get three execution attempts total. Permanent failures stop immediately. After final failure, preserve the last valid draft, show the seller the reason, and offer **Try again**, which starts a new job against the current draft.
- If the seller edits the draft while a job is running, keep the edits and treat the old result as based on an earlier revision. Offer **Run on latest draft** and wait for the seller to request it.
- Before the hosted demo, stop accepting local jobs on every stack and drain local jobs and broker messages. Shut down the local stacks after verifying the drain, then run the hosted stack in its own execution scope.
