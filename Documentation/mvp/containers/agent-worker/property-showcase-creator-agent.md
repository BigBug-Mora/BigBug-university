# Property Showcase Creator Agent

[Agent worker](agent-worker.md) · [Showcase Creator product behavior](../../agent-details/agent-details.md#5-property-showcase-creator-agent)

## Inputs and draft generation

Load the specific listing revision, approved facts available for publication, selected photos, and relevant inspector findings. For a revision, include the current showcase and newly approved public facts. Draft a headline, short description, highlights, and a full gallery in display order. The first gallery photo becomes the cover. Separately, select up to three distinct photos from that gallery for the featured story. Give each a title and a one- or two-sentence write-up. Ground the captions and write-ups in the associated photos or approved facts.

Preserve approximate values and seller attribution when relevant. Use inspector findings to improve gallery choices or identify gaps. Keep missing information unknown and restrict output to approved publishable facts. Exclude phone numbers, exact location, buyer-restricted answers, and draft-only notes from all public-facing draft fields, including captions.

## Validation and handoff

Validate that the result fits the expected structure, references allowed media, and makes supported claims. Check that each featured photo appears in the same gallery and that its story position is unique. If validation fails, report the issue while preserving the last valid draft. Submit a valid result to [Property service](../property-service.md) as an editable draft, with its source revision and stable job ID. The [Seller Agent](../agent-api/seller-agent.md) presents it for owner review. Preserve the current public page until an authorized seller publishes the new revision.

Verify missing values, approximate measurements, attempted use of buyer-restricted facts, duplicate delivery, and a late result after the owner edits the draft. Check that the current public page remains stable during generation and review.
