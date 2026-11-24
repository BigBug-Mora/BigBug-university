# Property Inspector Agent

[Agent worker](agent-worker.md) · [Inspector product behavior](../../agent-details/agent-details.md#4-property-inspector-agent)

## Inputs and evidence

Use the draft revision, property type, structured facts, and photo references from [Property service](../property-service/property-service.md). Retrieve the authorized photo set for that revision. Track which photos were actually reviewed so the result can distinguish a missing view from an image that could not be read.

## Review

- Identify reviewable quality problems such as dark, blurred, or repeated images.
- Suggest helpful missing views for the property type. For houses, consider the kitchen, bathrooms, exterior, main gate, and parking where relevant. For land, consider the entrance, access road, and plot views. For apartments, consider the kitchen, bathrooms, living area, and entry.
- Flag unclear or inconsistent claims for the seller to review. Describe visible evidence as observations. A photo of a road supports asking about access. Precise width, legal access, boundaries, and ownership require other evidence.
- For a draft with zero photos, return a missing-photo suggestion and suitable listing completeness findings. If photos were expected but could not be loaded, surface that as a processing issue.

## Output and handoff

Return each finding with its category, associated photo or field where applicable, observation, uncertainty, and suggested next action. Save it with the job and inspected revision. The [Seller Agent](../agent-api/seller-agent.md) presents it as optional. The [Showcase Creator](property-showcase-creator-agent.md) may use the evidence to organize the draft and preserve unknowns. An inspection leaves listing facts and publication unchanged.

Test dark and repeated photos, missing suggested views across all three property types, zero photos, unavailable photos, and a result produced after the seller changes the photo set.
