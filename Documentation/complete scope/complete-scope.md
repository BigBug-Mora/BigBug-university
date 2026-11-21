# EstateFlow AI Complete Product Scope

EstateFlow AI is the working name for the team's selected multi-agent real estate marketplace. This document is the reference for the full product scope. The team will define the competition MVP in a separate discussion.

- **Document Type** · Updated Project Concept and Detailed Idea Handover
- **Competition** · Innodata AI Catalyst 2026 — University Track
- **Initial Intended Market** · Sri Lanka
- **Proposed Competition Category** · AI & Robotic Engineering (not formally assigned)
- **Working Product Name** · EstateFlow AI (placeholder, not confirmed)
- **Project Status** · REAL ESTATE CONCEPT SELECTED BY THE TEAM. Individual features and product decisions remain open for refinement.
- **Scope of This Document** · Product vision, user problems, experiences, AI-agent responsibilities, trust and privacy, representative journeys, scope priorities, and important open questions. This is an idea-level handover, not an implementation specification.

## Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Origin of the Idea and the User Problem](#2-origin-of-the-idea-and-the-user-problem)
- [3. Product Vision and Boundaries](#3-product-vision-and-boundaries)
- [4. Intended Users](#4-intended-users)
- [5. Specialized Agents](#5-specialized-agents)
- [6. Seller Agent](#6-seller-agent)
- [7. Buyer Agent](#7-buyer-agent)
- [8. Property Inspector Agent](#8-property-inspector-agent)
- [9. Property Showcase Creator Agent](#9-property-showcase-creator-agent)
- [10. Market Intelligence Agent](#10-market-intelligence-agent)
- [11. Property Pricing and Comparables Agent](#11-property-pricing-and-comparables-agent)
- [12. Shared Property Knowledge and Repeated Questions](#12-shared-property-knowledge-and-repeated-questions)
- [13. Seller Insights and Buyer Feedback](#13-seller-insights-and-buyer-feedback)
- [14. Location Privacy and Disclosure Control](#14-location-privacy-and-disclosure-control)
- [15. Property Viewing Appointments](#15-property-viewing-appointments)
- [16. Cross-Agent Coordination and Human Decisions](#16-cross-agent-coordination-and-human-decisions)
- [17. End-to-End Flagship User Story](#17-end-to-end-flagship-user-story)
- [18. Trust, Accuracy, Privacy, and Limitations](#18-trust-accuracy-privacy-and-limitations)
- [19. Marketplace Experience and Screens](#19-marketplace-experience-and-screens)
- [20. Multi-Agent Rationale](#20-multi-agent-rationale)
- [21. Competition Context and Product Scope](#21-competition-context-and-product-scope)
- [22. Open Product Questions](#22-open-product-questions)
- [23. Product Summary](#23-product-summary)
- [24. Guidance for Future Scope Decisions](#24-guidance-for-future-scope-decisions)
- [Proposal Appendix](#proposal-appendix)

## 1. Executive Summary

Our selected idea is an independent, AI-powered real estate marketplace in which multiple specialized AI agents help property owners market properties and help potential buyers discover, understand, assess, and inquire about those properties.

The aim is not to build another website where sellers upload advertisements and buyers scroll through them.

The broader vision is to give every seller an AI-powered sales support team and every buyer an AI property discovery and research assistant. These agents cooperate when a task requires information or decisions from both parties.

Sellers should be able to explain a property conversationally, provide photographs and documents, obtain suggestions for incomplete or unclear information, receive an attractive and shareable property page, answer buyer inquiries efficiently, control private-information disclosure, see meaningful buyer-interest insights, and approve property-viewing appointments.

Buyers should be able to describe what they want in natural language, including nuanced needs that ordinary filters cannot easily express. They can compare listings, ask detailed property questions, explore the surrounding area, request missing or private information, evaluate asking prices, investigate possible land uses, and request viewings.

The marketplace must retain the value of a straightforward listing platform. AI assists the workflow but should not block a seller merely because photographs, measurements, or documents are missing.

Missing details should be identified honestly, and the listing should improve over time through seller input and buyer questions.

### Core Capabilities

- Independent public property marketplace for residential land, houses, and apartments.
- Conversational Seller Agent for onboarding and ongoing listing management.
- Conversational Buyer Agent that interprets requests, searches real listings, ranks relevant results, compares properties, and explains uncertainty.
- Property Inspector Agent for photo quality, relevant missing views, listing completeness, and inconsistencies.
- Property Showcase Creator Agent for trustworthy descriptions and well-organized, shareable property pages.
- Core Market Intelligence Agent for area information, economic context, historical trends, infrastructure, and potential land use.
- Core Property Pricing & Comparables Agent for advertised property price comparisons, comparable listings, and carefully qualified pricing analysis.
- Cross-agent requests for missing information, grouped so sellers are not repeatedly asked the same question.
- Knowledge reuse: seller answers become available to subsequent authorized buyers, subject to seller-controlled visibility.
- Seller insight summaries describing repeated questions, buyer concerns, and useful improvement suggestions.
- Privacy-aware answers about locations and private property information.
- Calendly-like viewing requests with seller confirmation before a booking is final; optional phone contact only with permission.

The innovation is the coordinated property journey: discovering a listing, identifying an information gap, asking the right person once, preserving the answer, serving multiple buyers appropriately, and improving the listing—all while keeping people in control of significant decisions.

We do not promise that a property will sell, that an investment will appreciate, that AI can establish legal ownership, or that a plot is officially approved for a particular use.

The system should provide evidence, meaningful assistance, and honest limits.

## 2. Origin of the Idea and the User Problem

### 2.1 Seller Experience and Fragmentation

The idea comes partly from firsthand frustration with the process of selling land and houses in Sri Lanka.

An owner may advertise a property on ikman.lk, Facebook Marketplace, social groups, specialized listing sites, or through personal contacts, yet still have to manage almost every task individually.

An advertisement may remain online for a long period without a successful sale.

Challenges commonly worth investigating include:

#### A. Repetitive and mixed-quality inquiries

Some buyers are serious, some are casually researching, and some messages are unrelated to a purchase.

Sellers repeat explanations about prices, area, road access, utilities, room features, location, documents, and appointments.

The system should organize inquiries without disrespecting people who are early in their search.

#### B. Incomplete advertisements

An ordinary owner may not know which facts buyers need.

A house listing may omit whether every bathroom is tiled, how many rooms have attached bathrooms, or what is visible in the backyard.

A land listing may omit road width, trees, water source, access conditions, or useful views of the entrance and surroundings.

Missing photos should trigger helpful suggestions, never a blanket ban on publication.

#### C. Weak marketing and presentation

Unclear captions, poor lighting, repeated pictures, missing highlights, disorganized galleries, or descriptions that are too short can make it difficult to understand a property.

The seller should be able to obtain professional-looking presentation without hiring a full marketing team.

#### D. Fragmented communication

Answers may be scattered across phone calls, WhatsApp conversations, comments, and separate platforms.

Even when a seller has already answered a common question, future buyers may not see the answer.

#### E. Little explanation of buyer interest

Sellers might know how many people contacted them but not which concerns recur.

Several people asking about water access, flood history, tiled bathrooms, or price negotiation may signal a useful information gap, not necessarily a defect.

#### F. Appointment friction

Buyers and sellers repeatedly suggest dates and times.

A seller may publish general availability but not actually be free on a particular day.

Showing an available slot must not be treated as guaranteed seller confirmation.

#### G. Lack of market context

The seller may not know how their asking price compares with advertised nearby properties, or whether an apparent market trend is supported by credible information.

### 2.2 Buyer Experience and Fragmented Evidence

Buyers may have to browse many inconsistent advertisements, compare incomplete facts, and contact owners just to learn basic details.

Their needs are often more complicated than location, property type, and budget.

Illustrative buyer requests:

- "Find land near Gampaha, 15–25 perches, under Rs. 20 million, with good road access but not beside a noisy main road."
- "I need a three-bedroom house with parking; are all the bathrooms tiled?"
- "Does this land have coconut, mango, or other established trees?"
- "Can I grow particular crops here? What about water access and the likely setup costs?"
- "Is this location practical for a small warehouse or another industrial activity?"
- "How far is this property from a main road, town, school, or hospital?"
- "How do recent asking prices in this area compare, and what do historical indicators show?"
- "The address is private. What can you tell me about the surrounding area without revealing it?"

The buyer must be able to tell whether an answer is a seller statement, a photograph-based observation, an external research finding, an estimate, or simply unknown.

### 2.3 Underlying Problem

Property buying and selling is a connected process rather than a single listing transaction:

Prepare information → Publish → Discover → Evaluate → Ask questions → Resolve gaps → Share approved information → Arrange a visit → Learn from buyer feedback → Improve the listing.

Traditional listing pages may support pieces of this journey, but the team's hypothesis is that coordinated AI assistance could reduce effort and information gaps across the whole journey.

This remains a hypothesis that should be researched rather than presented as an established universal fact.

### 2.4 Research We Still Need

Firsthand experience does not establish how widespread these problems are.

The team should investigate seller and buyer workflows, repeated questions, time spent responding, trust in AI responses, existing competitor capabilities, market data coverage, costs of operation, and whether users would use the proposed features.

## 3. Product Vision and Boundaries

### 3.1 The Independent Marketplace

The product should be usable as a real estate marketplace in its own right.

It should include listings, property detail pages, image galleries, seller and buyer accounts, search, saved interests or requests where useful, seller dashboards, and viewing requests.

It does not depend on importing listings from Facebook or ikman to function.

Owners may share a generated EstateFlow property page through permitted outside channels.

### 3.2 AI-First but Not AI-Only

The principal discovery journey should be conversational.

A buyer describes a goal; the Buyer Agent interprets the request and finds matching properties from actual platform records.

It can refine the search, explain tradeoffs, identify missing facts, and ask appropriate follow-up questions.

The system may retain simple browse controls and optional conventional filters for accessibility and convenience.

"AI-powered searching" does not mean the AI should invent properties or perform basic database calculations less reliably than ordinary software.

### 3.3 Core Product Principles

- Never invent property facts to make listings sound better.
- Do not prevent publishing just because some useful information or photographs are missing; make incompleteness visible and suggest improvements.
- Preserve where a statement came from and whether it has been independently verified.
- Keep exact locations, contact details, and documents under seller-controlled permissions.
- Ask sellers once for equivalent missing information when possible; reuse approved answers responsibly.
- Let owners approve consequential changes and disclosures.
- Treat market estimates and possible land uses as research, not guarantees or professional certification.
- Provide attractive, practical pages that owners can share.
- Keep brokers outside the initial product scope.
- Prioritize connected user value over having an unnecessarily large number of agents.

## 4. Intended Users

### 4.1 Individual Property Sellers

Initially, property owners selling land, houses, or apartments in Sri Lanka.

They may have limited marketing experience and may use phones as their primary device.

Their goals include publishing without difficulty, presenting a property accurately, avoiding repeated answers, protecting privacy, seeing interested-buyer trends, and handling viewings efficiently.

### 4.2 Property Buyers

Buyers seeking a home, residential land, an apartment, investment property, agricultural land, or land that might support a commercial or industrial purpose.

Their questions may involve purchase decisions, suitability, practical access, costs, or local conditions.

The system should help with research while distinguishing information from advice requiring a qualified professional.

### 4.3 Brokers

Brokers are not included in the current product scope.

The team should not design broker-specific agents, workflows, commissions, or dashboards in this version.

## 5. Specialized Agents

The following are intended roles within the product vision.

Some functions may be performed by conventional services rather than needing a separate reasoning agent in a first demonstration.

### Seller Agent

Conversational assistant for the owner; onboarding, inquiries, seller decisions, summaries, and delegation.

### Buyer Agent

Natural-language discovery, property-specific Q&A, comparison, research requests, and buyer-side communication.

### Property Inspector Agent

Inspection of photographs and available listing details for missing views, unclear presentation, and possible inconsistencies.

### Property Showcase Creator Agent

Trusted descriptions, highlights, gallery organization, and page presentation.

### Market Intelligence Agent

Area context, historical indicators, public infrastructure research, geographic context, and exploratory land-use assessments.

### Property Pricing & Comparables Agent

Comparable advertised-property research, asking-price comparisons, price normalization, and uncertainty-aware price context.

### Supporting Functions

Cross-user request coordination, a shared property knowledge record, privacy and approval controls, appointment management, and seller insight summaries.

These supporting functions do not all need to be marketed as separate AI agents.

## 6. Seller Agent

### 6.1 Conversational Listing Creation

An owner might say:

> "I want to sell my 20-perch land near Gampaha for 18 million rupees."

The assistant asks useful questions about the approximate area, road access, water, electricity, existing trees, photographs, available documents, permitted public details, and intended use, without demanding every possible answer at once.

For a house, it can ask about bedrooms, bathrooms, parking, tiled rooms, living spaces, garden, age, utilities, and condition.

For apartments it can ask about floor level, unit area, facilities, parking, maintenance-related details, and access.

What it asks should reflect the property type and previous answers.

A field may be: seller-provided, photograph-suggested, missing, uncertain, independently supported, public, or restricted.

> "Seller confirmed" must not automatically mean "independently verified."

### 6.2 Working With Specialists

After photographs are uploaded, the Seller Agent requests review from the Property Inspector and receives a usable summary.

It then asks the Showcase Creator to arrange an informative property page.

The owner sees suggestions, can correct details, and controls publication and consequential edits.

### 6.3 Incoming Buyer Requests

The Seller Agent receives grouped requests rather than treating every buyer question as an entirely new task.

It should help the seller identify what is missing, answer it once, and decide who may see the answer.

For instance, three buyers ask about access-road width using different wording.

The system recognizes the shared gap and presents one request to the seller.

Once the owner replies, other interested buyers may receive the answer if sharing is allowed.

### 6.4 Seller Insights

The owner can ask:

> "What did people want to know this week?"

> "Why do buyers keep asking about water?"

> "What should I improve?"

The assistant can summarize recurring questions, topics, voluntarily stated preferences or concerns, unanswered requests, appointment interest, and recurring missing information.

It should make measured suggestions, such as:

> "Several buyers asked about access-road width; consider including the measurement."

It should not conclude "your price is too high" or "your property has a defect" merely from a small number of questions.

It should not reveal other buyers' private conversations unnecessarily.

### 6.5 Owner Control

The Seller Agent may prepare suggestions and coordinate work, but cannot independently change asking prices, disclose restricted data, represent legal verification, accept binding offers, or finalize an appointment without seller approval.

## 7. Buyer Agent

### 7.1 Natural-Language Search Is the Default

The buyer can express requirements conversationally rather than choosing from a rigid collection of filters.

The agent identifies price range, geography, property type, size, must-have features, softer preferences, and intended use.

It searches actual marketplace listings, identifies matches, states which conditions are unmet or unknown, and explains any ranking or compromise.

Example:

> "I need at least 15 perches near Gampaha, under Rs. 20 million, suitable for a quiet family home, with a reasonable access road."

If "quiet" or "reasonable" cannot be established from available evidence, the agent should explain the uncertainty rather than silently assume a match.

### 7.2 Detailed Property Questions

The buyer should be able to ask natural, property-specific questions, for example:

> "Are all bedrooms tiled?"

> "Are the bathrooms fully tiled?"

> "Does the land have mango or coconut trees?"

> "Is there a well, piped water, or a different water source?"

> "Is there a separate entrance or enough room for parking?"

> "Is there an image of the backyard or kitchen?"

> "Does the entrance connect to a public road?"

The Buyer Agent checks seller-provided details, photographs, and authorized evidence.

A photo that does not show an amenity does not prove that it does not exist.

A photograph of one tiled room does not prove that every room is tiled.

Unanswered questions can be routed into the shared property-question process.

### 7.3 Property and Area Comparisons

The Buyer Agent can compare actual listings by asking price, size, rooms, parking, access, amenities, approximate location, and known conditions.

Comparisons should clearly show missing fields.

The agent can also bring in area or comparable-price research when relevant.

### 7.4 Land for Agriculture, Business, and Investment

A buyer may ask:

> "What could I grow here?"

> "How much water could those crops require?"

> "What might setup cost?"

> "Could a small factory or warehouse be appropriate?"

> "How has this area's land market changed?"

The Buyer Agent should consult specialized research rather than improvise.

It can bring together known property characteristics and external guidance, show relevant assumptions, and flag when a site visit, laboratory soil assessment, water study, legal review, planning approval, or qualified adviser is needed.

### 7.5 Buyer-Controlled Requests

If a fact is missing, the Buyer Agent offers to request it.

If a fact is known but restricted, it asks for permission through a distinct disclosure process.

A buyer should be able to track whether the answer is pending, available, declined, or no longer relevant.

### 7.6 Viewing Appointments

The Buyer Agent helps a user choose a proposed slot and request a viewing.

It must say "pending seller approval" until a seller explicitly accepts and the appointment is recorded as confirmed.

It may help with cancellations or alternative times without turning every scheduling step into a long conversation.

## 8. Property Inspector Agent

### 8.1 Purpose

The Inspector checks how clearly and completely the advertisement represents a property.

It is not a building inspector, surveyor, title examiner, or legal verifier.

### 8.2 Photograph Review

It can flag blurry, dark, overexposed, low-detail, repetitive, or poorly framed images.

It can suggest a clearer exterior, entrance, kitchen, living room, bedrooms, bathrooms, parking area, garden, or access-road image as relevant to a house.

For land, it might suggest entrance, access road, different viewpoints, visible boundaries, trees, and surroundings.

The list of useful views should vary with property type.

The system should recognize what has already been supplied and avoid asking for images that do not apply.

### 8.3 Listing-Information Checks

It can flag unknown road width, missing utilities, unclear dimensions, missing bathroom or room-finish details, or an absent apartment floor number.

It can also identify possible claims that lack illustration, e.g., "all bathrooms tiled" without relevant photographs.

This triggers a request for clarification or supporting media, not an accusation of dishonesty.

### 8.4 Publish First, Improve Continuously

A central design choice: sellers should generally be allowed to publish an incomplete listing, as long as basic required publication and safety rules are met.

Recommendations can appear as an optional improvement checklist and can be revisited when new buyer questions arise.

### 8.5 Limits

Visual evidence cannot prove ownership, title validity, parcel size, planning permissions, structural condition, flood safety, or complete coverage of an amenity.

The agent must communicate uncertainty.

## 9. Property Showcase Creator Agent

### 9.1 Purpose

Turn available, approved property facts into a clear and appealing page without inventing details.

### 9.2 Outputs

Potential outputs include a headline, concise description, key highlights, structured property facts, photograph captions, sensible gallery order, and an appropriate arrangement of details.

For land, emphasize extent, asking price, general location, access, trees or utilities if known, and relevant photos.

For houses, emphasize rooms, finishes, bathrooms, garden, parking, utilities, and interior/exterior photographs.

For apartments, emphasize unit size, level, rooms, parking, and building facilities.

### 9.3 Different Levels of Completeness

The page should be professional even if the seller has only a few photographs.

Missing detail should remain visibly unknown rather than being filled with attractive but fictional claims.

The agent can propose enhancements as more facts become available.

### 9.4 Approval and Sharing

The owner reviews descriptions and important edits.

After approval, the page can be shared through WhatsApp, social posts, messages, or other permitted channels without requiring the recipient to use the AI conversation experience.

## 10. Market Intelligence Agent

### 10.1 Why It Is Core

Buyers do not only ask:

> "What does this property contain?"

They ask:

> "What is this location like?"

> "What is changing nearby?"

> "Could I use this land for a purpose?"

> "How does the market in this area appear to be developing?"

These questions require research beyond the listing itself.

### 10.2 Research Themes

- General area characteristics and infrastructure, including roads, transport access, amenities, and relevant public information.
- Historical property-market trends where trustworthy data is available.
- Public economic indicators and market context, including Central Bank of Sri Lanka publications.
- Agricultural context, including agro-ecological zone, crop guidance, rainfall patterns, possible irrigation considerations, and other relevant publicly supported conditions.
- Land-use and industrial considerations such as access, utilities, planning categories, and permissions to investigate.
- Investment context and scenario-based explanations, not promises about appreciation.

### 10.3 Possible Source Categories

Central Bank of Sri Lanka indices and reports, relevant government land-use and mapping agencies, Department of Agriculture resources, other credible institutional publications, and authorized datasets.

A source should be judged for coverage, recency, geography, and what it actually measures.

Important distinction:

An indicator about Colombo District cannot automatically be treated as price history for a single plot in Gampaha.

A regional agricultural recommendation does not prove suitability of a particular parcel.

### 10.4 Example Research Interaction

Buyer:

> "Is this land suitable for growing coconuts, and what would initial cultivation cost?"

The agent identifies known area, size, soil or water information, and asks which details are missing.

It looks for relevant agricultural guidance and cost assumptions, then provides a qualified overview.

It should state that actual conditions, irrigation capacity, labour, current input costs, and expert field assessment can materially change the conclusion.

### 10.5 Industrial Use and Development

Buyer:

> "Can I put a warehouse or small industrial operation here?"

The research should discuss access, utilities, indicative area conditions, and regulatory questions to check.

It must not state that a development is legally permitted without the actual authoritative approval or suitable official evidence.

### 10.6 Uncertainty in Future Outcomes

Future land values, crop yields, operating costs, and area development are uncertain.

Where useful, provide assumptions and scenarios rather than presenting a precise prediction as a fact.

## 11. Property Pricing and Comparables Agent

### 11.1 Purpose

Help sellers and buyers understand advertised pricing in context.

This agent is essential to the intended product, not an optional extra.

### 11.2 Comparables

It can find appropriately sourced advertised properties with similar geographic areas, property types, sizes, access, and other available features.

It may compare asking price, price per perch or other relevant area measure, and explain how missing facts affect comparability.

Potential sources include approved or properly obtained data from real estate marketplaces such as ikman.lk, Facebook Marketplace where lawful and authorized access exists, other reputable listing sources, and the marketplace's own permitted information.

The concept does NOT assume that third-party marketplaces offer unrestricted API or scraping access.

Public visibility of an advertisement does not automatically grant permission to collect or reuse it in bulk.

### 11.3 Asking Price Versus Sale Price

Online advertised amounts are asking prices, not verified sale prices.

The agent must not quietly present them as transaction records.

Comparable listings may be outdated, duplicated, misleading, or unusually priced; the agent should explain this.

### 11.4 Historical Trends and Price Forecasts

It can work with the Market Intelligence Agent to explain official historical indices, local asking-price examples, time coverage, and wider conditions.

If future pricing scenarios are offered, the outcome must be shown as uncertain and assumption-dependent.

It is not a professional appraisal or investment guarantee.

### 11.5 Value for Sellers

For a seller, the agent might say:

> "Here are several relevant advertised properties and how their asking prices compare to yours. Differences in road access, area, and property type limit direct comparison."

It should never autonomously change a seller's asking price or assert a definitive "correct" valuation.

## 12. Shared Property Knowledge and Repeated Questions

### 12.1 Central Insight

Different buyers often ask the same underlying question in different words.

It is a poor experience if the Seller Agent asks the owner the identical question every time.

The platform should learn from previous approved answers and reduce repeated work.

### 12.2 Example

Buyer A asks:

> "How wide is the road?"

Buyer B asks:

> "Can you tell me the entrance road width?"

Buyer C asks:

> "Is the access road at least 15 feet?"

The system should identify a possible shared topic.

If road width is not known and there is already a pending seller request, additional buyers can be associated with that unresolved question rather than triggering duplicate prompts.

### 12.3 One Answer, Useful to Many Buyers

The seller replies, for example:

> "The road is approximately 15 feet wide."

The response is recorded as seller-provided, with its relevant qualifications.

Buyers waiting for that answer may be updated where they have opted in and are allowed to receive it.

Future inquiries can use the recorded answer.

### 12.4 Different Questions Must Remain Different

Questions that look similar may have different meaning.

"Road width", "Can a car enter?", and "Can a large truck turn in?" are related but not identical.

The system should not force one response to answer all three.

If the answer does not address the exact concern, the Buyer Agent should explain what remains unknown.

### 12.5 Seller Publication Preferences

After answering, the seller may choose whether that information is publicly visible, available to certain approved buyers, or retained only for private replies.

Newly learned knowledge must not automatically become public.

### 12.6 Continuous Listing Improvement

Repeated requests can prompt suggestions such as:

> "Add a bathroom photo."

> "Specify whether all rooms are tiled."

> "Clarify availability of water."

> "Describe the access road."

The seller remains in control of publication.

## 13. Seller Insights and Buyer Feedback

### 13.1 Purpose

Provide useful, non-invasive information about how potential buyers engage with a listing.

### 13.2 Potential Signals

Common questions; missing details; broad topics of interest; seller-approved follow-up responses; viewing requests; inquiries about access, price, water, documentation, trees, tiled rooms, or nearby facilities; and other properly collected activity.

### 13.3 Example

A seller receives a summary:

> "Many recent questions concern road access and water supply. A clearer entrance photo and water-source details could help buyers evaluate the listing."

Another summary might say:

> "Several visitors asked whether the bathrooms are tiled; the listing mentions three bathrooms but does not clarify finishes."

### 13.4 Responsible Interpretation

High inquiry volume does not guarantee demand, and a buyer question is not proof of a defect.

The system should avoid inventing buyers' intentions and avoid exposing identifying or private conversation details in aggregated summaries.

### 13.5 Relationship to Other Agents

The Seller Agent presents the insight.

The Inspector can identify missing evidence, the Showcase Creator can suggest a clearer presentation, and the buyer-question mechanism supplies the underlying recurring topics.

This is a coordinated feature, not necessarily a separate named AI agent.

## 14. Location Privacy and Disclosure Control

### 14.1 Seller-Defined Privacy

The seller should control what is public and what needs approval.

Public information might include district, approximate area, general property characteristics, asking price, and selected photos.

Restricted information might include exact address, coordinates, personal contact details, selected documents, and certain images.

### 14.2 Why Location Privacy Is More Than Hiding a Marker

A property may be locatable indirectly from repeated precise distance answers, distinctive nearby landmarks, map screenshots, image metadata, or combinations of clues.

The Buyer Agent must not reveal a hidden exact location through indirect responses.

### 14.3 Useful Answers Without Disclosing an Address

For buyers without permission, the system may provide a coarse general area, broader-area amenity descriptions, or approximate distances based on a public area rather than undisclosed precise property coordinates.

Such statements must be clearly labelled approximate and must not falsely imply property-level accuracy.

### 14.4 Example

Buyer:

> "How far is the land from the nearest main road?"

If its exact coordinates are public or the buyer has permission, the agent may provide an appropriate mapped distance with relevant caveats.

If the location is restricted, it can give only seller-approved general access information or invite the buyer to request permission.

It should not calculate and disclose many precise distances from the secret location.

### 14.5 Specific Disclosures

If a buyer asks for an exact location or private documents, the Seller Agent seeks approval.

Approval should be specific to the buyer, property, and information being shared, with sensible limits.

Approving one buyer must not grant access to everyone.

## 15. Property Viewing Appointments

### 15.1 Preferred Experience

Use a Calendly-like slot-selection interface rather than prolonged back-and-forth messaging.

But unlike a haircut booking, choosing a visible property-viewing slot does not automatically guarantee that the seller can attend.

### 15.2 Seller Availability

The seller can indicate generally suitable days and times, block inconvenient periods, and update availability.

These are candidate appointment windows, not unconditional promises.

### 15.3 Buyer Request

The buyer selects a suitable slot and submits a viewing request.

The screen clearly displays:

> "Awaiting seller confirmation."

### 15.4 Seller Decision

The seller can confirm, decline, or propose another time.

A request becomes a confirmed appointment only after seller approval and a final conflict check.

Both parties receive the result and can see their requests and appointments.

### 15.5 Changes and Failure Cases

The experience should address overlapping requests, seller non-response, cancellation, rescheduling, appointment reminders, and expiring unconfirmed requests.

A buyer should never be told that an appointment is confirmed when it is still pending.

### 15.6 Optional Calling

A seller can choose to allow phone contact or a platform-mediated call request.

If calling is not permitted, the Buyer Agent must not reveal the phone number.

Contact preferences can differ by property or situation.

### 15.7 Appointment Versus Location Permission

A confirmed appointment does not by itself mean unrestricted location or contact disclosure.

Those permissions should be handled deliberately, at an appropriate stage, with the seller's approval.

## 16. Cross-Agent Coordination and Human Decisions

### 16.1 Why Coordination Matters

The platform's central experience depends on specialized assistants collaborating while representing different people and different permitted interests.

The Buyer Agent may need a missing answer.

The Seller Agent may need to ask the owner.

The Inspector may discover a photo gap.

The Showcase Creator may propose an edit based on new information.

### 16.2 Typical Missing-Information Exchange

Buyer asks → Buyer Agent checks available property knowledge → Missing fact identified → Existing pending request checked → Seller Agent presents a consolidated question → Seller responds → Answer recorded with sharing rules → Buyer Agent follows up → Listing improvement suggested if appropriate.

### 16.3 Restricted Information Is Different

A missing fact and a hidden fact are not the same thing.

For a missing fact, the seller needs to provide the answer.

For a restricted fact, the seller may need to authorize sharing an already known answer.

The system should manage those separately.

### 16.4 Persistent Requests

A question or approval request should not disappear when either user closes the app.

The buyer can return to see its status; the seller can respond later.

A previous approval should not be silently applied to unrelated information or users.

### 16.5 Human Oversight

The seller controls publication, sensitive disclosures, asking-price changes, and viewing confirmation.

Buyers control their own requests and whether they wish to receive updates.

AI may recommend and coordinate, but should not make binding property commitments on behalf of either party.

### 16.6 What Is an AI Agent?

Not every function requires its own AI agent.

Appointment conflict checks, permissions, and simple status changes can be ordinary product features.

Specialized AI roles are justified where interpretation, research, multimodal review, synthesis, or context-aware coordination materially helps the user.

The project should explain the actual collaboration instead of counting named modules.

## 17. End-to-End Flagship User Story

All property details and responses in this section are illustrative, not verified real properties or research findings.

### Step 1: Owner Creates a Land Listing

An owner advertises 20 perches near Gampaha, asking Rs. 18 million.

They upload five photographs.

The exact location is private; road width is not yet supplied.

The owner also mentions that several fruit trees grow on the land but does not know all their varieties.

### Step 2: Inspection Without Blocking Publication

The Property Inspector notices that the entrance image is dark, the road width is unspecified, and there is no clear photo showing the trees.

The Seller Agent suggests improvements, but the seller may publish a truthful, appropriately labelled listing now.

### Step 3: Showcase Page

The Showcase Creator organizes the approved images, generates a concise description, highlights the stated land extent and asking price, and labels the approximate location.

The seller reviews the page and shares it.

### Step 4: Buyer Searches With a Complex Request

A buyer says:

> "Find 15–25 perch land around Gampaha below Rs. 20 million, away from busy roads, with potential for a small garden or crops."

The Buyer Agent searches actual records and shows this property as a possible match while noting that quietness, exact access, and crop suitability have not been established.

### Step 5: Buyer Asks About Access and Trees

The buyer asks whether a car can enter and which trees are planted.

The Buyer Agent answers only what is known.

It offers to request more specific access and tree information.

### Step 6: Multiple Buyers Share One Information Gap

Another buyer has already asked about road width.

Rather than generate duplicate seller messages, the system groups equivalent unanswered road-width questions.

It still recognizes that truck turning space is a different question.

### Step 7: Seller Answers Once

The Seller Agent asks the owner.

They reply:

> "The access road is approximately 15 feet wide; I believe there are two mango trees and some coconut trees."

The system labels this as seller-provided information, including uncertainty.

It does not transform "I believe" into a verified botanical inventory.

### Step 8: Authorized Knowledge Is Reused

Buyers who requested this public-approved detail can receive the answer.

The Buyer Agent can answer future equivalent inquiries without asking the owner again.

### Step 9: Buyer Asks About Agriculture and Pricing

The buyer asks whether a particular crop might grow there and how the asking price compares with other properties.

The Market Intelligence Agent supplies qualified regional guidance; the Pricing Agent provides appropriately sourced advertised comparables.

Both explain assumptions and limits.

Neither promises cultivation success or future appreciation.

### Step 10: Buyer Asks for Exact Location

The address is restricted.

The Buyer Agent does not reveal it, including by giving precise landmark distances.

The Seller Agent presents an approval request.

The owner grants limited access to that buyer only.

### Step 11: Listing Gets Better

The system suggests adding the newly supplied access-road information and a clearer entrance photo.

The seller approves a suitable public update.

Other viewers can now understand the listing better.

### Step 12: Buyer Requests a Viewing

The buyer sees candidate time slots, requests Saturday morning, and receives a pending status.

The seller explicitly approves that time; only then does the platform mark it confirmed.

If phone contact or the exact address is needed, those permissions are handled separately.

### Step 13: Seller Receives Useful Insights

The seller asks what buyers care about.

The Seller Agent summarizes repeated questions about access, trees, and water, as well as viewing requests.

It suggests information improvements without claiming to know exactly why the property has or has not sold.

### Why This Story Matters

It demonstrates a coherent marketplace experience, real property discovery, differentiated agent responsibilities, questions answered from a growing knowledge record, fewer duplicate seller interruptions, external research where relevant, guarded disclosure, human decisions, and an appointment that truly requires confirmation.

## 18. Trust, Accuracy, Privacy, and Limitations

### 18.1 Property Information Should Be Traceable

A statement can originate from the seller, an uploaded image, a document, a credible third-party source, or a computed estimate.

Those sources carry different levels of certainty.

The interface should help buyers distinguish them.

### 18.2 Images and Documents Have Limits

Images may reveal visible features but cannot prove legal title, exact boundaries, building safety, soil quality, or unseen conditions.

Uploaded documents cannot be assumed authentic solely because a seller provided them.

### 18.3 Research Is Not Certification

Land valuation, crop planning, water availability, expected plantation cost, industrial suitability, and investment forecasts can be sensitive decisions.

The platform may give useful preliminary research, but decisions may require licensed professionals, physical inspections, authoritative records, and current permissions.

### 18.4 Protect Private Information

Exact locations, contact details, documents, and certain photographs require deliberate disclosure choices.

Permissions should apply only to the intended audience.

Responses, previews, map displays, and summaries must respect the same restrictions.

### 18.5 Trust and Misuse

A mature platform would also need to address fake advertisements, impersonation, misleading claims, duplicate listings, abusive requests, and inappropriate access to owner details.

A competition demonstration may use explicitly fictional or authorized samples and should not pretend these challenges have been fully solved.

## 19. Marketplace Experience and Screens

### 19.1 Public Marketplace

An inviting home page with property cards, images, general location, asking price, category, conversational discovery, and clear paths to property pages.

Browsing should remain easy for users who do not wish to chat.

### 19.2 Property Page

Clear headline, approved gallery, structured facts, distinction between known and unknown information, public area description, question interface, request-information action, permission-aware location handling, and viewing-request action.

It should work well as a shared link.

### 19.3 Seller Experience

Overview of published properties and pending tasks; conversational listing assistant; listing-preview and improvements; grouped unanswered buyer questions; approval requests; appointments; and aggregated buyer-interest insights.

### 19.4 Buyer Experience

Conversational search, relevant listings, comparisons, property-specific conversations, research summaries, saved inquiries, request statuses, location-permission requests, and viewing requests.

### 19.5 Design Priorities

Clarity, mobile usability, trustworthy labeling, readable photographs, understandable AI explanations, accessible options, sensible notifications, and obvious pending/approved states.

AI should reduce user effort, not make a simple action unnecessarily complicated.

## 20. Multi-Agent Rationale

### 20.1 Distinct Responsibilities

The Buyer Agent interprets buyer needs; the Seller Agent represents the owner's available information and approvals; the Inspector critiques listing completeness; the Showcase Creator improves presentation; the Market Intelligence Agent brings outside context; and the Pricing Agent compares advertised values.

### 20.2 Meaningful Collaboration

Their cooperation changes user outcomes.

For example, a buyer asks a question; the system finds the knowledge gap; the Seller Agent gathers an approved response; the Buyer Agent relays it; the Inspector and Showcase Creator identify a useful listing improvement; seller insights track the repeated topic.

These tasks connect rather than merely running unrelated chatbots.

### 20.3 Potential Benefits and Honest Tradeoffs

Specialization may improve appropriate data access, clarity of responsibilities, trust, traceability, and handling of different kinds of questions.

It may also add complexity, delays, cost, and opportunities for conflicting responses.

A strong AI Catalyst project needs to demonstrate value rather than assume that more agents are inherently better.

## 21. Competition Context and Product Scope

### 21.1 Selection and Category

The team has selected the real estate ecosystem as its AI Catalyst University Track project.

The working category recommendation is AI & Robotic Engineering because the main contribution concerns cooperating intelligent agents, not physical robots.

Real estate is not itself one of the eight industry labels in the supplied guide, so the category should not be presented as formally approved.

A team member previously asked an organizer whether real estate could be submitted in AI & Robotic Engineering or Logistics.

The response emphasized that the system's core should be strong and scalable and expressed flexibility in category choice.

This was encouraging but not a formal category assignment.

### 21.2 Long-Term Vision Versus Initial Competition Demonstration

The whole ecosystem is the selected product concept.

The first demonstrable version should focus on a few connected experiences that work convincingly, particularly seller onboarding, photo/listing review, AI-driven discovery, coordinated missing-information requests, authorized response reuse, location privacy, seller-approved viewing requests, and one or two grounded market-research examples.

Advanced crop-specific financial modelling, industrial planning, and long-horizon investment forecasting remain part of the intended capability set but depend on reliable data and appropriate safeguards.

Treat them as ambitions that may initially be demonstrated through clearly bounded examples rather than falsely claiming broad expertise.

### 21.3 What the Judges Should Understand

The platform is not just a polished real estate website with chatbots.

Its core proposition is that specialized AI assistants cooperate in a durable buyer–seller workflow, improve property knowledge over time, and reduce repetitive work while respecting human decisions.

The concept must ultimately be supported by real demonstrations and fair comparisons, although detailed testing and engineering choices are outside this idea-level document.

## 22. Open Product Questions

These are not reasons to reopen the project selection; they are decisions to refine during planning.

- What minimum information is genuinely required to publish safely, and what can remain unknown?
- How should owners review photo-based suggestions without feeling penalized for incomplete uploads?
- How should semantically similar questions be grouped without conflating different buyer needs?
- When should a seller's answer become public, buyer-specific, or confidential?
- How should the product show price research when suitable comparables are sparse or inconsistent?
- Which official sources provide sufficiently local, current evidence for a given agricultural or industrial question?
- What approximate location information is useful without revealing a protected address?
- How long should a proposed viewing slot remain pending before it expires?
- How should buyers be informed when sellers do not respond?
- Which user journeys offer the clearest benefit during the first competition demonstration?

## 23. Product Summary

EstateFlow AI (working title) is the selected idea for an independent multi-agent real estate marketplace initially aimed at Sri Lanka.

A seller receives an AI sales assistant, listing-completeness guidance, attractive presentation, coordinated inquiries, controlled information disclosure, buyer-interest insights, and confirmation-based property-viewing management.

A buyer receives natural-language property discovery, detailed property Q&A, fair comparisons, guided market and price research, preliminary land-use investigation, and convenient ways to request additional details or viewings.

The system should never force an owner to wait for a perfectly complete advertisement before listing.

It should help the listing improve as real questions arise.

Repeated buyer questions are recognized and consolidated so the owner can answer once where appropriate, and answers are reused only with the correct visibility permissions.

Market Intelligence and Pricing & Comparables are CORE agents, not optional future agents.

Brokers remain outside scope.

The preferred viewing flow is Calendly-like slot selection followed by REQUIRED seller confirmation; phone contact is optional and permission-controlled.

AI powers discovery and interpretation, while straightforward product operations should remain dependable and understandable.

The central product promise is not a guaranteed sale or investment return.

It is a more informative, organized, responsive, and trustworthy property marketplace through meaningful collaboration between specialized AI assistants and human users.

## 24. Guidance for Future Scope Decisions

- Treat the real estate ecosystem as the team's SELECTED IDEA.
- Do not revert to wording that it is merely one candidate among alternatives.
- The working name, competition category, final agent boundaries, and detailed product decisions are still subject to refinement.
- Keep the discussion centered on the real estate product.
- Distinguish user-facing features from claims that require evidence, and distinguish the long-term product vision from what can realistically be demonstrated first.
- Do not reintroduce brokers in the current scope.
- Do not demote Market Intelligence or Pricing & Comparables to optional features.
- Preserve the AI-first natural-language discovery experience, the non-blocking listing-improvement principle, repeated-question consolidation, seller insights, privacy-aware geographic answers, and seller-confirmed appointment slots.
- Do not invent property facts, market statistics, user research findings, actual comparable prices, agricultural outcomes, planning permissions, verified ownership, or guaranteed investment returns.
- Treat third-party marketplace access as conditional on authorization and applicable rules.
- Keep human decisions central to sensitive disclosures and consequential actions.
- This document describes WHAT we want to build and WHY.
- It deliberately avoids prescribing a technical stack, unit-testing methodology, detailed infrastructure, or low-level implementation choices.

## Proposal Appendix

This appendix preserves the Markdown proposal, including its research evidence, proposed architecture, and evaluation plan.

### **EstateFlow AI**

Multi-Agent AI-Powered Real Estate Ecosystem

**INNODATA AI CATALYST 2026  |  UNIVERSITY TRACK  |  PROJECT PROPOSAL**

GitHub repository: [https://github.com/BigBug-Mora/BigBug-university](https://github.com/BigBug-Mora/BigBug-university)

#### **1. Problem Definition and Context**

Property discovery and selling are not isolated listing tasks. They involve preparing advertisements, interpreting buyer preferences, supplying missing information, evaluating locations and prices, managing privacy, and arranging visits. These activities are often fragmented across listing websites, messaging applications, calls, and manual follow-up.

Seller-side friction. Owners must prepare adequate photographs and descriptions, respond to recurring questions, coordinate appointments, and interpret buyer interest without a consolidated record. Weak or incomplete listings make it difficult for prospective buyers to assess suitability before contacting the seller.

Buyer-side friction. Buyers encounter uneven listing details, inconsistent descriptions, unsuitable results from simple filters, and gaps in facts such as road access, utilities, potential land uses and precise locations. Comparing properties or obtaining answers often requires repeated contact.

Root cause. Conventional marketplaces primarily organize advertisements; they do not consistently coordinate ongoing information exchange, property research and seller-controlled decisions between buyers and owners.

##### **Stakeholders, urgency and objective**

The initial stakeholders are individual property owners and prospective buyers. Online discovery makes photographs and property information central to decision-making; neither improved search filters nor isolated chatbots solve persistent knowledge gaps and multistep coordination. Recent progress in tool-using and multimodal AI makes these coordinated workflows feasible to evaluate.

EstateFlow AI proposes an independent marketplace where sellers receive AI-assisted listing and inquiry management, buyers receive conversational property discovery and research, and specialized agents collaborate through traceable workflows with human approvals. The aim is improved information quality and coordination—not guaranteed sales or certified legal, financial or physical assessments.

#### **2. Research Findings and Global Relevance**

International studies show that photographs, details and reliable disclosure matter in online property markets. The three local discussion screenshots below offer qualitative context; user research and controlled tests will establish whether similar needs are widespread.

International evidence. In the US National Association of REALTORS® 2025 survey, 81% of internet-using home buyers rated photographs very useful and 77% rated detailed property information very useful \[1\]. These results concern US buyers and cannot be interpreted as Sri Lankan prevalence figures.

Academic and institutional evidence. Hebdzyński (2023) identified information gaps and mismatches between written descriptions and photographs in Polish apartment listings \[2\]. A European consumer study found that 22% of surveyed recent buyers/renters had encountered missing information about property damage, and 17% reported missing or misleading energy-performance information \[3\]. These findings demonstrate challenges outside Sri Lanka, not local prevalence.

##### **Qualitative observations from Sri Lanka**

These individual comments illustrate specific frustrations; they are not representative survey findings.

![Figure 1](images/figure-1.png)

*Figure 1. Sri Lankan seller listings criticized for missing photos, details and phone-call requirements \[4\].*

![Figure 2](images/figure-2.png)

*Figure 2. Comment reporting missing prices, low-quality images and slow replies across local online marketplaces \[4\].*

![Figure 3](images/figure-3.png)

*Figure 3. Land seller seeking guidance on marketing, pricing and reaching prospective buyers \[5\].*

##### **Research interpretation and potential impact**

The evidence suggests listing completeness, repeated clarification and property comparison as priorities for user testing. Their prevalence and economic impact remain unmeasured.

#### **3. Proposed AI Solution**

EstateFlow AI combines a conventional property marketplace with AI-led seller and buyer experiences. Core listing, identity, permission and appointment records remain authoritative application data. Agents use approved records and research tools rather than inventing unsupported property facts.

##### **Seller experience**

- Conversational listing onboarding tailored to land, houses and apartments, recording unknown details instead of fabricating them.
- Photograph and listing-completeness analysis, followed by seller-reviewed descriptions and shareable property showcase pages.
- An AI sales assistant for inquiries, missing-information requests, viewing approvals and recurring buyer feedback.

##### **Buyer experience**

- AI-led natural-language discovery and cross-property comparison using structured data constraints plus semantic matching.
- Grounded property-specific answers, clearly distinguishing seller claims, externally supported facts and unresolved questions.
- Source-qualified market, price, geographic, agricultural and potential industrial-use research, including utilities, water, road access and investment context.
- Controlled requests for restricted property details and individual viewing slots, disclosed or confirmed only with seller approval.

##### **Reusable property knowledge**

Unknown questions are tracked per property. Equivalent future questions can reuse an authorized answer; the seller receives one consolidated request when new information is genuinely needed. Aggregated buyer concerns and recurring questions provide actionable seller insights without unnecessary disclosure of individual buyers' information.

#### **4. Project Objectives, Key Features and Expected Outcomes**

- Listing quality: identify missing information and image problems, then generate accurate owner-approved presentation.
- Buyer discovery: improve relevance of results for complex natural-language requirements while preserving factual filters.
- Inquiry efficiency: reduce duplicate seller requests and increase the reuse of authorized property knowledge.
- Decision support: deliver source-attributed market, property-price and possible land-use information with clear limitations.
- Trusted coordination: enforce seller-controlled information disclosure and explicit confirmation of viewing appointments.
- Measurable AI value: compare specialized multi-agent collaboration with a comparable single-agent system and human-executed tasks.

#### **5. Multi-Agent Architecture and Responsibilities**

The proposed system contains seven specialized AI roles. Roles reflect separate user interests, evidence domains and tasks; they need not map one-to-one onto independently deployed microservices.

**Seller Agent** — Represents the owner; gathers property details, coordinates listing inspection and showcase creation, handles missing-information requests, presents approval requests and summarizes buyer engagement.

**Buyer Agent** — Interprets conversational requirements, retrieves authorized listings, answers grounded questions, compares alternatives and delegates research or seller clarification.

**Property Inspector Agent** — Examines images and structured details for visual-quality problems, missing coverage and inconsistencies; does not claim professional physical or legal inspection.

**Property Showcase Creator Agent** — Produces accurate listing narratives and page configurations from approved facts and inspector recommendations; submits material changes for seller review.

**Market Research Agent** — Investigates area context, roads, infrastructure, utilities and potential agricultural or industrial uses, identifying evidence gaps and required official checks.

**Price Research Agent** — Examines available market indicators, comparable asking prices and historical data; distinguishes advertised prices from completed transactions and uncertain forecasts.

**Sales Intelligence Agent** — Identifies authorized inquiry patterns, recurring questions, buyer concerns and potential listing improvements, reporting aggregated insights to the seller.

##### **Communication, decision-making and human oversight**

The Buyer and Seller Agents interact through a coordination/workflow layer that routes typed requests, records their status and delegates specialist tasks. Research outputs contain citations, provenance and uncertainty indicators. Conflicting outputs are flagged for clarification or review rather than silently resolved. Seller decisions govern important listing changes, restricted-information disclosure, viewing confirmation and asking-price changes.

Deterministic application services enforce access permissions, idempotency and appointment states; they do not constitute an eighth AI agent. Agents receive only the information and tools appropriate to their responsibilities.

#### **6. Planned Technical Architecture and Workflow**

##### **Architecture**

EstateFlow AI adopts domain-oriented microservices separating property management, buyer–seller engagement and approvals, multi-agent execution, and research intelligence. Containerized FastAPI services coordinate through authenticated interfaces and asynchronous messaging. A Next.js application provides buyer and seller experiences. Persistent records, object storage and identity management use managed AWS services.

##### **Service boundaries and information flow**

The Property Service owns canonical listing records and seller-approved facts; the Engagement Service owns inquiries, approval requests and viewing states. The Agent Orchestration Service coordinates Buyer, Seller and specialist agents through LangGraph. The Research Service retrieves external evidence and returns source details, freshness and uncertainty. Services exchange structured requests rather than granting each agent unrestricted database access. FastAPI enforces identity, ownership and authorization before any restricted record is returned.

##### **Property knowledge and failure handling**

Each recorded answer is associated with its property, source, visibility level, update time and approval status. Semantically similar questions may retrieve a candidate answer, but the application checks permissions and validity before reuse. Unanswered requests are deduplicated so multiple buyers do not trigger repeated seller interruptions. RabbitMQ and Celery manage long-running tasks; persisted workflow state, idempotent operations and logged agent handoffs support recovery if external tools or model calls fail.

##### **Representative inter-agent workflow**

1. Seller Agent gathers property information → Property Inspector identifies visual or content gaps → Showcase Creator prepares the property page → seller reviews and approves publication.

2. Buyer Agent interprets a complex land request → retrieves authorized candidates → delegates market and price investigations → produces an evidence-qualified comparison.

3. Buyer asks an unanswered road-width question → property knowledge is checked → one structured request is opened if missing → Seller Agent obtains the answer → the authorized answer is stored and reused.

4. Buyer requests exact location or a viewing slot → seller explicitly approves the specific request → backend updates authorization or booking state → Buyer Agent communicates the confirmed outcome.

5. Sales Intelligence Agent analyzes permitted inquiry trends → Seller Agent receives recurring questions, concerns and listing-improvement recommendations.

##### **Technology stack**

- Frontend — Next.js, React, TypeScript, Tailwind CSS
- Backend and architecture — Python, FastAPI, Docker, Docker Compose; domain-oriented microservices
- Multi-agent orchestration and LLM abstraction — LangGraph, LangChain; initially Anthropic Claude API, with configurable OpenAI, Gemini and DeepSeek integrations
- Database and retrieval — Amazon RDS PostgreSQL, pgvector and an embedding model for semantic similarity
- Storage and identity — Amazon S3; Amazon Cognito with Auth.js; backend-enforced authorization
- Asynchronous processing and engineering — RabbitMQ, Celery, GitHub Actions, OpenTelemetry and structured logging

#### **7. Single-Agent Benchmarking and Evaluation**

The proposed multi-agent system will be evaluated against a fair single-agent baseline and human-assisted execution on the same documented scenarios. Tests will provide comparable starting facts, tools and information access. The multi-agent system will not receive privileged evidence unavailable to its baselines.

##### **Benchmark scenarios**

- Listing preparation — identify missing fields/photo problems and generate accurate, reviewed content.
- Complex buyer discovery — translate ambiguous requirements into relevant, actually listed properties.
- Missing information — recognize unknown facts, request clarification once, persist and reuse the approved answer.
- Research and comparison — produce sourced area/price assessments with calibrated uncertainty.
- Privacy and viewing — enforce disclosure restrictions and confirm only seller-approved appointments.
- Robustness — handle missing evidence, conflicting sources, failed tools, retries and repeated requests.

##### **Evaluation protocol and scoring**

For every test case, reviewers will define the input property records, permitted sources, expected decision and any facts intentionally left unknown. The evaluation will distinguish correct retrieval from plausible but unsupported answers. Property matches will be judged against documented buyer constraints; research answers will be checked for valid citations and price-source distinctions; and incomplete cases will be scored positively only when uncertainty is disclosed rather than guessed.

Privacy and coordination cases will check whether restricted addresses remain inaccessible without approval, whether viewing requests stay pending until the seller confirms them, and whether repeated equivalent questions generate at most one outstanding seller clarification. Execution traces will capture delegation paths, tool calls, errors, retries, latency and token use. Results will be reported per scenario as well as in aggregate so failures are not hidden by a single average.

##### **Adversarial and failure-recovery trials**

The test set will also include inaccurate or conflicting listing details, repeated inquiry submissions, interrupted research calls, outdated information and attempts to obtain private addresses through conversational prompts. Each scenario will specify an acceptable safe response: an unanswered fact remains unknown, a restricted field remains hidden, and a viewing stays unconfirmed without seller approval. These tests will assess whether specialized delegation introduces additional failure modes or helps isolate them.

Reviewers will examine the full sequence of agent messages and application-state changes, not merely the final answer. A recovered task must not create an additional seller request or appointment. A research result that lacks reliable evidence must be labeled inconclusive. Reports will distinguish AI accuracy from workflow correctness, record errors explicitly, and highlight cases where a simpler single-agent design is more effective.

##### **Baselines, metrics and validity**

Multi-agent baseline: specialist agents use one another's outputs through recorded delegations. Single-agent baseline: one general-purpose assistant operates with comparable tools, data and inference budget. Human baseline: team members perform standardized tasks manually with documented instructions and expertise. Repeated trials, common scoring rubrics, expected answers and execution traces will support evaluation without inventing results.

Metrics include task success and correctness; grounded-answer quality; retrieval relevance; source quality; unauthorized disclosure rate; duplicate seller requests; appointment-state correctness; latency; token/model expenditure; human time; tool failures and recovery. Human ratings will assess usefulness, clarity and misleading confidence. Results will report sample sizes and limitations.

A limited property dataset and small participant sample may not generalize to Sri Lanka. Human comparisons depend on experience; public asking prices differ from completed transactions; agricultural and industrial suitability may require on-site studies and regulatory checks. A larger agent count alone does not demonstrate superior performance.

#### **8. Ethics, Risks and Limitations**

##### **Privacy, accountability and reliability**

Seller-controlled information is classified as public, restricted or private. Exact locations, contact details and documents are disclosed only after server-side access checks tied to explicit permissions. Agents cannot bypass these controls, and private facts must not leak through inferred answers.

Property facts retain provenance: seller-provided, independently sourced, inferred, unknown or disputed. AI-generated listing content requires suitable review. Photograph interpretation cannot verify ownership, title, construction quality or surveyed boundaries.

Price research uses comparable advertised prices and applicable official indicators where available, never presenting listing prices as verified sales or its conclusions as certified valuations. Agricultural, industrial and investment findings are exploratory and do not replace professional assessments, permits or official planning decisions.

Persistent workflow states and audit logs protect against duplicate seller requests, unauthorized disclosure and double confirmation of appointments. Research and model failures must produce explicit uncertainty. Third-party data access and processing of personal information will follow applicable permissions and privacy safeguards.

##### **References**

\[1\] National Association of REALTORS® (2025). [2025 Profile of Home Buyers and Sellers](https://cmr.realtor/clientuploads/2025_Profile_of_Home_Buyers_and_Sellers.pdf).

\[2\] Hebdzyński, M. (2023). [Quality information gaps in housing listings: Do words mean the same as pictures? Journal of Housing](https://doi.org/10.1007/s10901-023-10043-z) and the Built Environment.

\[3\] European Commission (2018). [Consumer market study on the functioning of real estate services in the European Union](https://www.uni-bremen.de/fileadmin/user_upload/fachbereiche/fb6/fb6/Forschung/ZERP/TENLAW/FollowUp/real_estate_services_summary_EU_en_october_2018.pdf).

\[4\] u/Embarrassed\_Bat\_2157 (2025), r/srilanka. [Sri Lankan sellers on online marketplaces](https://www.reddit.com/r/srilanka/comments/1hu66yw/). Includes the discussion shown in Figures 1–2.

\[5\] u/No\_Reading\_9586 (2026), r/srilanka. [How can I effectively market and sell land in Sri Lanka, especially to serious buyers or investors? Figure 3.](https://www.reddit.com/r/srilanka/comments/1qmi12i/how_can_i_effectively_market_and_sell_land_in_sri/)
