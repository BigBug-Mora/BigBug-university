# Property Service Container

[Container directory](../containers.md) · [MVP agent behavior](../../agent-details/agent-details.md)

## Runtime and owned data

Run a Python FastAPI application with SQLAlchemy access to the property records in shared RDS PostgreSQL. Own draft and public listing state, property type and structured facts, photo metadata, showcase revisions, and publication decisions. S3 holds the image bytes. Cognito identifies the acting user for authorized operations.

## Operations

| Operation | Required behavior |
| --- | --- |
| Create or edit a draft | Check seller ownership. Support houses, land, and apartments. Preserve unknown fields, source, and qualifiers. Identify the revision used by specialist jobs. |
| Select facts for the page | Save changes to page visibility as a new listing revision. Freeze its selected versions and approvals for preview and publication. |
| Register and validate facts | Resolve agent-proposed definitions against existing fields and keys. Register new ordinary facts with their applicability. For supported dedicated keys use allowlisted, typed setters and field-only readers. Save the covered count in its existing revision column with its total-parking constraint. Return only the approved key's value and evidence from a shared revision. |
| Upload or read photos | Authorize the action for a specific listing and object. Issue short-lived scoped access. Before attaching an upload, verify it belongs to the authorized draft and satisfies the agreed file rules. An incomplete upload must stay out of the listing gallery. |
| Read a public listing or search | Return published records through the public projection. Apply structured filters and preserve unknown values. Private fields and draft-only materials stay out of public results. |
| Read the property detail page | Return public facts from the published listing revision and the matching showcase's cover, featured photo story, and full gallery. Return featured photos in story order and gallery photos in display order. |
| Supply workflow context | Give the [Agent API](../agent-api/agent-api.md) or [Agent Worker](../agent-worker/agent-worker.md) the facts and authorized photos needed for that operation. Provide approved coarse location information when a question can be answered safely. |
| Apply a showcase result | Accept a validated result as an editable draft tied to its source revision and job identity. Save the showcase, gallery, and featured photo story in one transaction. Preserve the last valid draft if generation fails. Handle a result from an older revision without overwriting a newer draft. |
| Publish | Verify seller ownership, the explicit approval, the target revision, and the agreed minimum fields. Update the public projection consistently. Inspection suggestions are optional. |
| Manage private details | Check seller ownership and store each current encrypted value under a stable detail ID. Edit the value in place. On removal, clear the value and retire the ID permanently. Adding another detail in the same slot creates a new ID. Serialize phone changes with publication and keep at least one active number on a published listing. |

## Interactions and rule enforcement

The [Frontend](../frontend/frontend.md) uses the listing and upload operations. The agent containers use the same domain rules for AI-assisted reads and writes. An approved inquiry answer belongs to [Engagement service](../engagement-service/engagement-service.md). Property owns the immutable structured value. Share answer updates the draft and buyer-visible fact through a narrow Property operation within the Engagement transaction. Publish updates the buyer-visible pointers for changed public facts in the same transaction as the publication pointer. See the [database contracts](../../database/contracts.md#which-value-a-buyer-sees). For a protected buyer read, resolve only the detail IDs Engagement authorized for that buyer and listing. Check the listing, kind, and active state before returning a current value.

Keep searchable facts separate from derived suggestions. Use revision checks for conflicting seller edits. Use stable operation identifiers for retryable registration, result submission, and publication. Log safe record identifiers and outcome codes for upload, draft, and publish failures.

Verify that an unauthorized user cannot read another seller's draft or media, that failed uploads stay out of the gallery, that a delayed result cannot replace a newer showcase, and that an owner can publish after ignoring optional suggestions when the required fields are present. Test that edits preserve the detail ID and retired IDs stay inactive when their slot is reused. Confirm photo size and type rules before implementation.
