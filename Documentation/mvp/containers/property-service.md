# Property Service Container

[Container directory](containers.md) · [MVP agent behavior](../agent-details/agent-details.md)

## Runtime and owned data

Run a Python FastAPI application with SQLAlchemy access to the property records in shared RDS PostgreSQL. Own draft and public listing state, property type and structured facts, photo metadata, showcase revisions, and publication decisions. S3 holds the image bytes. Cognito identifies the acting user for authorized operations.

## Operations

| Operation | Required behavior |
| --- | --- |
| Create or edit a draft | Check seller ownership. Support houses, land, and apartments. Preserve unknown fields, source, and qualifiers. Identify the revision used by specialist jobs. |
| Upload or read photos | Authorize the action for a specific listing and object. Issue short-lived scoped access. Before attaching an upload, verify it belongs to the authorized draft and satisfies the agreed file rules. An incomplete upload must stay out of the listing gallery. |
| Read a public listing or search | Return published records through the public projection. Apply structured filters and preserve unknown values. Private fields and draft-only materials stay out of public results. |
| Supply workflow context | Give the [Agent API](agent-api/agent-api.md) or [Agent Worker](agent-worker/agent-worker.md) the facts and authorized photos needed for that operation. Provide approved coarse location information when a question can be answered safely. |
| Apply a showcase result | Accept a validated result as an editable draft tied to its source revision and job identity. Preserve the last valid draft if generation fails. Handle a result from an older revision without overwriting a newer draft. |
| Publish | Verify seller ownership, the explicit approval, the target revision, and the agreed minimum fields. Update the public projection consistently. Inspection suggestions are optional. |

## Interactions and rule enforcement

The [Frontend](frontend.md) uses the listing and upload operations. The agent containers use the same domain rules for AI-assisted reads and writes. An approved inquiry answer belongs to [Engagement service](engagement-service.md). Incorporating that fact into the public listing requires a separate authorized listing change. Any operation that retrieves an exact location for a buyer must enforce the relevant disclosure permission through the agreed protected read path.

Keep searchable facts separate from derived suggestions. Use revision checks for conflicting seller edits. Use stable operation identifiers for retryable registration, result submission, and publication. Log safe record identifiers and outcome codes for upload, draft, and publish failures.

Verify that an unauthorized user cannot read another seller's draft or media, that failed uploads stay out of the gallery, that a delayed result cannot replace a newer showcase, and that an owner can publish after ignoring optional suggestions when the required fields are present. Minimum publication fields, photo size and type rules, and the protected detail storage and retrieval contract still need confirmation.
