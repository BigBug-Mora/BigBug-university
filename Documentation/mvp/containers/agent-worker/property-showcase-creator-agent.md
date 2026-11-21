# Property Showcase Creator Agent

[Agent worker](agent-worker.md) · [Showcase Creator product behavior](../../agent-details/agent-details.md#5-property-showcase-creator-agent)

## Inputs and draft generation

Load the specific listing revision, approved facts available for publication, selected photos, and relevant inspector findings. For a revision, include the current showcase and newly approved public facts. Use one MVP showcase template with a headline, short description, highlights, and ordered photo references. Captions must be grounded in the associated photo or approved facts.

Preserve approximate values and seller attribution when relevant. Use inspector findings to improve gallery choices or identify gaps. Keep missing information unknown and restrict output to approved publishable facts. Exclude phone numbers, exact location, buyer-restricted answers, and draft-only notes from all public-facing draft fields, including captions.

## Validation and handoff

Validate that the result fits the expected structure, references allowed media, and makes supported claims. If validation fails, report the issue while preserving the last valid draft. Submit a valid result to [Property service](../property-service.md) as an editable draft, with its source revision and stable job ID. The [Seller Agent](../agent-api/seller-agent.md) presents it for owner review. Preserve the current public page until an authorized seller publishes the new revision.

Verify missing values, approximate measurements, attempted use of buyer-restricted facts, duplicate delivery, and a late result after the owner edits the draft. Check that the current public page remains stable during generation and review.
