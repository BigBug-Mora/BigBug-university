# EstateFlow AI MVP Agent Details

Use this document as the build reference for the four AI agents and their handoffs in the MVP. The [complete product scope](../../complete%20scope/complete-scope.md) covers the wider marketplace. This document records the team's four-agent MVP direction and the behavior each agent must support. Examples use fictional property data. The fields described here express the information that must travel between components. See the [MVP technology stack](../teach-stack/tech-stack.md) for model, storage, orchestration, and deployment choices. Exact schemas and UI design remain implementation decisions.

See the [container overview](../containers/containers.md) for runtime responsibilities and open decisions. The [Agent API](../containers/agent-api/agent-api.md) runs the [Seller Agent](../containers/agent-api/seller-agent.md) and [Buyer Agent](../containers/agent-api/buyer-agent.md) interactions. The [Agent worker](../containers/agent-worker/agent-worker.md) runs the [Property Inspector](../containers/agent-worker/property-inspector-agent.md) and [Property Showcase Creator](../containers/agent-worker/property-showcase-creator-agent.md) jobs in the proposed layout.

## 1. MVP workflow

The MVP supports **houses, land, and apartments**. Seller onboarding, photo review, showcase generation, buyer discovery, and property questions work for all three. The relevant listing fields and photo suggestions vary by property type.

An owner describes a property and supplies available photos. The Seller Agent gathers the facts and requests a review. The Property Inspector Agent returns photo and listing findings. The Property Showcase Creator Agent uses those findings and approved facts to draft a page. The owner reviews and publishes it. The Buyer Agent finds the listing from a natural-language search and answers property questions. If a buyer requests a missing fact, the Seller Agent collects an answer for owner approval. Authorized buyers can reuse that answer. The owner can also approve adding it to the public showcase if its visibility permits.

The four AI agents in this workflow are the **Seller Agent**, **Property Inspector Agent**, **Property Showcase Creator Agent**, and **Buyer Agent**. A backend workflow coordinator manages their handoffs. Market Intelligence and Pricing & Comparables remain core agents in the full product scope. This document leaves their MVP implementation open, along with viewing and other marketplace workflows beyond the four-agent journey.

## 2. Rules shared by all four agents

- Use the application records and approved inputs for property facts. Carry the source and qualifiers into any generated answer or draft. “Approximately 15 feet” stays approximate, and “the owner believes” stays attributed.
- Treat **unknown** as a valid outcome. An omitted field or an unseen feature in a photo does not establish that the feature is absent. Flag unclear or conflicting evidence for owner review before publishing or reusing a claim about it.
- Track **source**, **certainty**, **visibility**, and **approval** independently. A seller-provided statement can be approximate, restricted, and approved at the same time. Seller approval grants the specified use of the fact. Independent verification requires independent evidence.
- Treat owner replies, listing text, and uploaded media as inputs to interpret. Application permissions and approval rules apply regardless of any instructions embedded in those inputs.
- Keep public pages, buyer responses, and shared traces within their permitted visibility. The backend supplies each agent with the information relevant to its task and filters what may leave that context.
- Keep listing phone numbers, the written address, and the map pin private. Handle phone and exact-location requests separately. A seller can select the specific details to share with one buyer for one listing.
- A private-detail grant lets the buyer see the current value of the shared detail after edits. Removing the detail makes it unavailable to recipients. Adding a detail in the same slot requires a new grant. Check permissions before returning protected details or answers.
- Require a product action from the owner for publication, material listing changes, and disclosure. A draft, a suggested edit, and a proposed answer remain pending until the relevant approval is recorded.

## 3. Seller Agent

**Purpose.** Be the owner's conversation interface for listing preparation, improvement, and buyer inquiries.

**Inputs.** Owner messages, the property type and current draft, uploaded photos or photo references, inspection findings, the showcase draft, and pending requests for the owner's property.

**Behavior**

1. Extract structured facts the owner actually supplied, such as general location, asking price, and type-specific details. Ask about plot size, access, and utilities for land, rooms and parking for houses, and unit size, floor, and facilities for apartments where relevant. Preserve earlier answers and leave unanswered fields unknown.
2. Request a review of the current draft and available photos. Present the Inspector's findings in an optional improvement checklist. The owner can ignore any suggestion and continue with an incomplete listing once the application's basic publication requirements are met.
3. Request a showcase draft using the approved listing facts and relevant findings. Present it for the owner to edit and approve before publication.
4. Show an always-current in-app summary of unanswered questions grouped by property and underlying fact. For example, show “3 buyers asked about access-road width” as one item. A request appears as soon as a buyer confirms it. The owner can answer from the summary, decline, or leave it pending. Interpret any reply as a proposed answer and ask for clarification if it is ambiguous or conflicts with the record.
5. Ask the owner to confirm the proposed answer and who may see it. Submit that decision to the backend. A public listing edit is a separate approval from sharing an answer in an inquiry.

**Outputs and handoffs.** Proposed changes to the listing facts, follow-up questions, inspection and showcase requests, and proposed answers with the supporting owner reply and intended visibility. After approval, the Seller Agent passes the structured answer to the backend for storage. The approval allows the Buyer Agent to deliver the answer back into the original property chat of each requesting buyer who is authorized to see it. For a declined request, the Buyer Agent communicates the declined status without disclosing any private information.

**Example.** If the owner says, “The access road is roughly 15 feet, I think,” propose *about 15 feet, seller-provided and approximate*. If the reply refers to the main road and the inquiry refers to the access road, ask which road the owner means.

## 4. Property Inspector Agent

**Purpose.** Review the quality and completeness of the advertisement using one pass over the current draft and available photos.

**Inputs.** Property type, structured listing details, draft claims, and uploaded image references. Findings must refer to the draft and images reviewed.

**Behavior**

- Flag visible quality problems such as darkness, blur, or repetition, and identify missing views that would help explain the property. Examples by type:
  - **House:** Kitchen, bathrooms, front exterior, main gate, and parking when relevant.
  - **Land:** Plot entrance or main gate, access road, and views of the plot from useful angles.
  - **Apartment:** Kitchen, bathrooms, living area, and unit entrance or other relevant access views where the owner can share them.
- Flag missing facts or potential inconsistencies between the listing and the supplied evidence. Phrase image findings as observations. A visible entrance may justify asking about road access. It cannot establish road width, legal access, exact boundaries, ownership, or development permissions.
- Suggest practical improvements, such as retaking a dark entrance photo or adding a clear view of the access road. If there are no photos, return a missing-photo suggestion and any applicable listing completeness findings.

**Outputs and handoffs.** Each finding identifies the issue, the relevant photo or field when available, what the evidence supports, and a suggested next step. The Seller Agent presents the suggestions to the owner, who decides which are worth acting on. The Showcase Creator uses the findings to organize the draft and preserve unknown fields. Findings cannot publish, edit, or verify a property fact.

**Example.** “The entrance photo is dark. The road width is still unknown. Ask the owner for a measurement and suggest a clearer entrance photo.”

## 5. Property Showcase Creator Agent

**Purpose.** Turn approved, publishable facts and photos into an editable listing draft using one showcase template.

**Inputs.** The property record, facts available for publication, selected photos, and the Inspector's findings. For a revision, also use the current showcase and any newly approved public facts.

**Behavior**

- Draft a headline, short description, highlights, and a suggested gallery order. Use the first gallery photo as the cover. Select up to three distinct gallery photos for a separately ordered featured story and give each a title and a one- or two-sentence write-up. Ground captions and write-ups in the associated photos or approved facts.
- Use review findings to choose clearer photos, suggest a replacement, or keep a material detail visibly unknown. Preserve the owner's qualifiers on measurements, features, and other uncertain claims.
- Return changes for owner review. Keep the approved public page stable while a draft or material revision is pending. A fact shared with a particular buyer stays out of the public draft unless the owner separately approves it for publication.

**Outputs and handoffs.** An editable draft with sections and photo references, plus any remaining information gaps for the seller. Return it to the Seller Agent and seller interface. The application creates or updates the public page after the owner's publication decision.

**Example.** Use the approved plot area, asking price, and general location in the page. Leave “Access road width” as unknown until the owner approves a publishable answer.

## 6. Buyer Agent

**Purpose.** Help buyers discover actual marketplace listings and get grounded answers about a property.

**Inputs.** The buyer's search or property question, identity and applicable access context supplied by the backend, published listing records, and approved facts available to that buyer.

**Behavior**

1. In **Search mode**, interpret natural-language requests into hard requirements and preferences. Search published houses, land, and apartments using those criteria. Explain what matches, what fails a requirement, and what is unknown. For example, show a listing with unknown vehicle access as needing confirmation when access is a must-have.
2. Selecting a property opens **Property Chat**, scoped to that listing's ID. Answer only about that property using permitted evidence, with provenance and uncertainty. Keep materially different questions separate. “How wide is the access road?” and “Can a large truck turn in?” require different evidence. **Back to Search** returns the buyer to the previous query and results, where they can continue or start a new search.
3. If a fact is missing, offer to request it. Queue the request as soon as the buyer confirms. If an equivalent request is already pending, attach this inquiry to it without prompting the owner again. If a previous equivalent request was declined, a later confirmed inquiry can create a new request. Show the status in Property Chat and keep the original decline in its history.
4. When an answer has been saved and approved, use the backend to check who can see it and post it in each authorized requesting buyer's original Property Chat. Read the current buyer-visible fact from Property for each fresh question, including a follow-up in an older chat. If the request was declined, report the status. If the evidence remains missing or conflicted, or the buyer lacks approval, explain what remains unresolved.
5. Answer ordinary location questions using approved approximate area information or a coarse result derived by a backend service. Keep raw coordinates, exact addresses, and phone numbers out of ordinary chat context. Avoid precise distances or distinctive landmark clues derived from a protected location.
6. Provide separate **Request phone number** and **Request exact location** buttons on the property page. When the buyer asks for either in chat, show the corresponding action there. Both entry points use the same permission flow, and clicking the action submits the request. The owner decides independently for each requested detail. If approved, show the value in a dedicated request result for that buyer and let the Buyer Agent tell them it is available there. Pending and declined results show status only.

**Outputs and handoffs.** Structured search criteria, grounded listing recommendations, buyer-facing answers and request status, and requests to the seller workflow for a missing fact or permission. The application determines which records and request results the buyer can access.

**Example.** “The seller says the access road is about 15 feet wide. There is no confirmed measurement of space for a large truck to turn.”

## 7. Workflow coordinator and shared records

The **workflow coordinator** is the middle layer between the agents. It runs the handoffs, persists their state, and records what happened. The Seller Agent owns the conversation with the owner. The backend calls the specialist at the appropriate step and applies application rules independently of any model output.

| Workflow | Handoff | Application responsibility |
| --- | --- | --- |
| Inspect a draft | Seller Agent → Inspector → Seller Agent | Load the current draft and its photos, save findings against that draft, and present them as suggestions. |
| Generate or revise a showcase | Seller Agent → Showcase Creator → owner | Supply publishable facts and relevant findings, save the generated draft, and publish only after approval. |
| Clarify a missing fact | Buyer Agent → Seller Agent → owner | Queue after buyer confirmation, preserve each buyer's inquiry and original chat, and show one entry per pending property fact in the live seller summary. A declined request stays closed, and a later confirmed inquiry can create a new entry. |
| Approve and reuse an answer | Owner → Seller Agent → property knowledge → Buyer Agent | Save the approved answer with its source, qualifiers, and visibility. Deliver it in the original chats of authorized requesting buyers, and recheck current permission on subsequent reads. |
| Request phone number or exact location | Property button or Buyer Agent → Seller Agent → owner | Keep disclosure requests distinct from missing-fact requests. Apply each grant to the intended buyer, property, and requested detail. Return an approved value through the dedicated request result. |

The core records the implementation needs are a **listing**, **property facts**, **inspection findings**, a **showcase draft and publication state**, **information requests**, and **owner decisions**. Keep references between related records. For example, a request identifies the property, the fact being requested, its type and status, and the buyers associated with it. An approved answer retains the owner as its source, the approved value and qualifiers, visibility, and the decision that allows reuse.

Make handoffs safe to repeat. A retry or a concurrent equivalent inquiry should leave one outstanding seller request for that fact. Record enough trace information to connect a workflow to the responsible agent, its relevant inputs and outputs, and the resulting state change. Use safe references or redacted values for restricted data in reviewable traces. If a specialist call fails, keep the last valid draft or request state and let the user retry from there.

## 8. Acceptance examples

| Scenario | Expected behavior |
| --- | --- |
| Owner supplies a dark entrance photo and leaves road width blank | Inspector flags both gaps. Showcase draft preserves the unknown width. The owner may publish once the basic requirements are met. |
| House photos omit the kitchen, bathroom, and main gate | Seller Agent presents the applicable suggestions as optional checklist items. Ignoring them does not block publication. |
| Buyer searches for a plot with confirmed vehicle access | A listing with unknown access is presented as unresolved for that requirement. |
| Buyer selects an apartment from search | Property Chat answers about that apartment only. Back to Search restores the prior query and results. |
| Two buyers submit equivalent access-road width questions | The live seller summary shows one item for both inquiries. A separate question about truck turning space remains distinct. |
| Owner replies “about 15 feet” before approving it | Buyers see the pending state. After approval, authorized requesting buyers receive the approximate, attributed answer in their original chats. |
| Owner declines a question or leaves it pending | The buyer sees the corresponding status and receives no property detail from that request. |
| A buyer confirms a new inquiry after an equivalent one was declined | A new request enters the seller summary. The original inquiry still shows its declined status. |
| Owner only authorizes a specific buyer | That buyer can obtain the answer. Other buyers and the public showcase cannot see it. |
| Owner edits a shared phone number, written address, or map pin | The approved buyer sees the updated value in the same protected result. |
| Owner removes a shared detail and adds another in the same slot | The previous result shows the removed detail as unavailable. Sharing the new detail requires a new grant. |
| Buyer asks for a phone number in chat and requests the exact location from the property page | Chat offers the phone request action. Each action opens its own permission request. If only location is approved, the authorized buyer can see it in the dedicated result while the phone number remains hidden. |
| Owner approves adding the width to the public page | The Showcase Creator can prepare the revision. The published page reflects it after the publication decision is recorded. |
| The application restarts or retries after a saved request | The request remains available and the retry does not create a duplicate. |

For evaluation, compare the four-agent workflow, a single agent with comparable data, tools and permissions, and a human following the same scenarios. Score **listing preparation** and **missing-information resolution** separately. Check output correctness, provenance, agreement between the displayed and stored state, duplicate requests, unauthorized disclosure, time, and cost. Preserve a trace of both specialist handoffs and the cross-user clarification.

## 9. Decisions left to the implementation plan

- Minimum publication fields, pilot inventory, and representative photo fixtures for houses, land, and apartments.
- Exact request and result schemas, and visibility choices for ordinary factual answers.
- How agent modules and shared code are organized within the FastAPI backend.
- The benchmark fixtures, number of trials, and scoring thresholds. See the [proposal appendix](../../complete%20scope/complete-scope.md#proposal-appendix) for the original evaluation plan.
