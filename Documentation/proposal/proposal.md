# **EstateFlow AI**

Multi-Agent AI-Powered Real Estate Ecosystem

**INNODATA AI CATALYST 2026  |  UNIVERSITY TRACK  |  PROJECT PROPOSAL**

GitHub repository: [https://github.com/BigBug-Mora/BigBug-university](https://github.com/BigBug-Mora/BigBug-university)

## **1. Problem Definition and Context**

Property discovery and selling are not isolated listing tasks. They involve preparing advertisements, interpreting buyer preferences, supplying missing information, evaluating locations and prices, managing privacy, and arranging visits. These activities are often fragmented across listing websites, messaging applications, calls, and manual follow-up.

Seller-side friction. Owners must prepare adequate photographs and descriptions, respond to recurring questions, coordinate appointments, and interpret buyer interest without a consolidated record. Weak or incomplete listings make it difficult for prospective buyers to assess suitability before contacting the seller.

Buyer-side friction. Buyers encounter uneven listing details, inconsistent descriptions, unsuitable results from simple filters, and gaps in facts such as road access, utilities, potential land uses and precise locations. Comparing properties or obtaining answers often requires repeated contact.

Root cause. Conventional marketplaces primarily organize advertisements; they do not consistently coordinate ongoing information exchange, property research and seller-controlled decisions between buyers and owners.

### **Stakeholders, urgency and objective**

The initial stakeholders are individual property owners and prospective buyers. Online discovery makes photographs and property information central to decision-making; neither improved search filters nor isolated chatbots solve persistent knowledge gaps and multistep coordination. Recent progress in tool-using and multimodal AI makes these coordinated workflows feasible to evaluate.

EstateFlow AI proposes an independent marketplace where sellers receive AI-assisted listing and inquiry management, buyers receive conversational property discovery and research, and specialized agents collaborate through traceable workflows with human approvals. The aim is improved information quality and coordination—not guaranteed sales or certified legal, financial or physical assessments.

## **2. Research Findings and Global Relevance**

International studies show that photographs, details and reliable disclosure matter in online property markets. The three local discussion screenshots below offer qualitative context; user research and controlled tests will establish whether similar needs are widespread.

International evidence. In the US National Association of REALTORS® 2025 survey, 81% of internet-using home buyers rated photographs very useful and 77% rated detailed property information very useful \[1\]. These results concern US buyers and cannot be interpreted as Sri Lankan prevalence figures.

Academic and institutional evidence. Hebdzyński (2023) identified information gaps and mismatches between written descriptions and photographs in Polish apartment listings \[2\]. A European consumer study found that 22% of surveyed recent buyers/renters had encountered missing information about property damage, and 17% reported missing or misleading energy-performance information \[3\]. These findings demonstrate challenges outside Sri Lanka, not local prevalence.

### **Qualitative observations from Sri Lanka**

These individual comments illustrate specific frustrations; they are not representative survey findings.

![Figure 1](images/figure-1.png)

*Figure 1. Sri Lankan seller listings criticized for missing photos, details and phone-call requirements \[4\].*

![Figure 2](images/figure-2.png)

*Figure 2. Comment reporting missing prices, low-quality images and slow replies across local online marketplaces \[4\].*

![Figure 3](images/figure-3.png)

*Figure 3. Land seller seeking guidance on marketing, pricing and reaching prospective buyers \[5\].*

### **Research interpretation and potential impact**

The evidence suggests listing completeness, repeated clarification and property comparison as priorities for user testing. Their prevalence and economic impact remain unmeasured.

## **3. Proposed AI Solution**

EstateFlow AI combines a conventional property marketplace with AI-led seller and buyer experiences. Core listing, identity, permission and appointment records remain authoritative application data. Agents use approved records and research tools rather than inventing unsupported property facts.

### **Seller experience**

- Conversational listing onboarding tailored to land, houses and apartments, recording unknown details instead of fabricating them.
- Photograph and listing-completeness analysis, followed by seller-reviewed descriptions and shareable property showcase pages.
- An AI sales assistant for inquiries, missing-information requests, viewing approvals and recurring buyer feedback.

### **Buyer experience**

- AI-led natural-language discovery and cross-property comparison using structured data constraints plus semantic matching.
- Grounded property-specific answers, clearly distinguishing seller claims, externally supported facts and unresolved questions.
- Source-qualified market, price, geographic, agricultural and potential industrial-use research, including utilities, water, road access and investment context.
- Controlled requests for restricted property details and individual viewing slots, disclosed or confirmed only with seller approval.

### **Reusable property knowledge**

Unknown questions are tracked per property. Equivalent future questions can reuse an authorized answer; the seller receives one consolidated request when new information is genuinely needed. Aggregated buyer concerns and recurring questions provide actionable seller insights without unnecessary disclosure of individual buyers' information.

## **4. Project Objectives, Key Features and Expected Outcomes**

- Listing quality: identify missing information and image problems, then generate accurate owner-approved presentation.
- Buyer discovery: improve relevance of results for complex natural-language requirements while preserving factual filters.
- Inquiry efficiency: reduce duplicate seller requests and increase the reuse of authorized property knowledge.
- Decision support: deliver source-attributed market, property-price and possible land-use information with clear limitations.
- Trusted coordination: enforce seller-controlled information disclosure and explicit confirmation of viewing appointments.
- Measurable AI value: compare specialized multi-agent collaboration with a comparable single-agent system and human-executed tasks.

## **5. Multi-Agent Architecture and Responsibilities**

The proposed system contains seven specialized AI roles. Roles reflect separate user interests, evidence domains and tasks; they need not map one-to-one onto independently deployed microservices.

**Seller Agent** — Represents the owner; gathers property details, coordinates listing inspection and showcase creation, handles missing-information requests, presents approval requests and summarizes buyer engagement.

**Buyer Agent** — Interprets conversational requirements, retrieves authorized listings, answers grounded questions, compares alternatives and delegates research or seller clarification.

**Property Inspector Agent** — Examines images and structured details for visual-quality problems, missing coverage and inconsistencies; does not claim professional physical or legal inspection.

**Property Showcase Creator Agent** — Produces accurate listing narratives and page configurations from approved facts and inspector recommendations; submits material changes for seller review.

**Market Research Agent** — Investigates area context, roads, infrastructure, utilities and potential agricultural or industrial uses, identifying evidence gaps and required official checks.

**Price Research Agent** — Examines available market indicators, comparable asking prices and historical data; distinguishes advertised prices from completed transactions and uncertain forecasts.

**Sales Intelligence Agent** — Identifies authorized inquiry patterns, recurring questions, buyer concerns and potential listing improvements, reporting aggregated insights to the seller.

### **Communication, decision-making and human oversight**

The Buyer and Seller Agents interact through a coordination/workflow layer that routes typed requests, records their status and delegates specialist tasks. Research outputs contain citations, provenance and uncertainty indicators. Conflicting outputs are flagged for clarification or review rather than silently resolved. Seller decisions govern important listing changes, restricted-information disclosure, viewing confirmation and asking-price changes.

Deterministic application services enforce access permissions, idempotency and appointment states; they do not constitute an eighth AI agent. Agents receive only the information and tools appropriate to their responsibilities.

## **6. Planned Technical Architecture and Workflow**

### **Architecture**

EstateFlow AI adopts domain-oriented microservices separating property management, buyer–seller engagement and approvals, multi-agent execution, and research intelligence. Containerized FastAPI services coordinate through authenticated interfaces and asynchronous messaging. A Next.js application provides buyer and seller experiences. Persistent records, object storage and identity management use managed AWS services.

### **Service boundaries and information flow**

The Property Service owns canonical listing records and seller-approved facts; the Engagement Service owns inquiries, approval requests and viewing states. The Agent Orchestration Service coordinates Buyer, Seller and specialist agents through LangGraph. The Research Service retrieves external evidence and returns source details, freshness and uncertainty. Services exchange structured requests rather than granting each agent unrestricted database access. FastAPI enforces identity, ownership and authorization before any restricted record is returned.

### **Property knowledge and failure handling**

Each recorded answer is associated with its property, source, visibility level, update time and approval status. Semantically similar questions may retrieve a candidate answer, but the application checks permissions and validity before reuse. Unanswered requests are deduplicated so multiple buyers do not trigger repeated seller interruptions. RabbitMQ and Celery manage long-running tasks; persisted workflow state, idempotent operations and logged agent handoffs support recovery if external tools or model calls fail.

### **Representative inter-agent workflow**

1. Seller Agent gathers property information → Property Inspector identifies visual or content gaps → Showcase Creator prepares the property page → seller reviews and approves publication.

2. Buyer Agent interprets a complex land request → retrieves authorized candidates → delegates market and price investigations → produces an evidence-qualified comparison.

3. Buyer asks an unanswered road-width question → property knowledge is checked → one structured request is opened if missing → Seller Agent obtains the answer → the authorized answer is stored and reused.

4. Buyer requests exact location or a viewing slot → seller explicitly approves the specific request → backend updates authorization or booking state → Buyer Agent communicates the confirmed outcome.

5. Sales Intelligence Agent analyzes permitted inquiry trends → Seller Agent receives recurring questions, concerns and listing-improvement recommendations.

### **Technology stack**

- Frontend — Next.js, React, TypeScript, Tailwind CSS
- Backend and architecture — Python, FastAPI, Docker, Docker Compose; domain-oriented microservices
- Multi-agent orchestration and LLM abstraction — LangGraph, LangChain; initially Anthropic Claude API, with configurable OpenAI, Gemini and DeepSeek integrations
- Database and retrieval — Amazon RDS PostgreSQL, pgvector and an embedding model for semantic similarity
- Storage and identity — Amazon S3; Amazon Cognito with Auth.js; backend-enforced authorization
- Asynchronous processing and engineering — RabbitMQ, Celery, GitHub Actions, OpenTelemetry and structured logging

## **7. Single-Agent Benchmarking and Evaluation**

The proposed multi-agent system will be evaluated against a fair single-agent baseline and human-assisted execution on the same documented scenarios. Tests will provide comparable starting facts, tools and information access. The multi-agent system will not receive privileged evidence unavailable to its baselines.

### **Benchmark scenarios**

- Listing preparation — identify missing fields/photo problems and generate accurate, reviewed content.
- Complex buyer discovery — translate ambiguous requirements into relevant, actually listed properties.
- Missing information — recognize unknown facts, request clarification once, persist and reuse the approved answer.
- Research and comparison — produce sourced area/price assessments with calibrated uncertainty.
- Privacy and viewing — enforce disclosure restrictions and confirm only seller-approved appointments.
- Robustness — handle missing evidence, conflicting sources, failed tools, retries and repeated requests.

### **Evaluation protocol and scoring**

For every test case, reviewers will define the input property records, permitted sources, expected decision and any facts intentionally left unknown. The evaluation will distinguish correct retrieval from plausible but unsupported answers. Property matches will be judged against documented buyer constraints; research answers will be checked for valid citations and price-source distinctions; and incomplete cases will be scored positively only when uncertainty is disclosed rather than guessed.

Privacy and coordination cases will check whether restricted addresses remain inaccessible without approval, whether viewing requests stay pending until the seller confirms them, and whether repeated equivalent questions generate at most one outstanding seller clarification. Execution traces will capture delegation paths, tool calls, errors, retries, latency and token use. Results will be reported per scenario as well as in aggregate so failures are not hidden by a single average.

### **Adversarial and failure-recovery trials**

The test set will also include inaccurate or conflicting listing details, repeated inquiry submissions, interrupted research calls, outdated information and attempts to obtain private addresses through conversational prompts. Each scenario will specify an acceptable safe response: an unanswered fact remains unknown, a restricted field remains hidden, and a viewing stays unconfirmed without seller approval. These tests will assess whether specialized delegation introduces additional failure modes or helps isolate them.

Reviewers will examine the full sequence of agent messages and application-state changes, not merely the final answer. A recovered task must not create an additional seller request or appointment. A research result that lacks reliable evidence must be labeled inconclusive. Reports will distinguish AI accuracy from workflow correctness, record errors explicitly, and highlight cases where a simpler single-agent design is more effective.

### **Baselines, metrics and validity**

Multi-agent baseline: specialist agents use one another's outputs through recorded delegations. Single-agent baseline: one general-purpose assistant operates with comparable tools, data and inference budget. Human baseline: team members perform standardized tasks manually with documented instructions and expertise. Repeated trials, common scoring rubrics, expected answers and execution traces will support evaluation without inventing results.

Metrics include task success and correctness; grounded-answer quality; retrieval relevance; source quality; unauthorized disclosure rate; duplicate seller requests; appointment-state correctness; latency; token/model expenditure; human time; tool failures and recovery. Human ratings will assess usefulness, clarity and misleading confidence. Results will report sample sizes and limitations.

A limited property dataset and small participant sample may not generalize to Sri Lanka. Human comparisons depend on experience; public asking prices differ from completed transactions; agricultural and industrial suitability may require on-site studies and regulatory checks. A larger agent count alone does not demonstrate superior performance.

## **8. Ethics, Risks and Limitations**

### **Privacy, accountability and reliability**

Seller-controlled information is classified as public, restricted or private. Exact locations, contact details and documents are disclosed only after server-side access checks tied to explicit permissions. Agents cannot bypass these controls, and private facts must not leak through inferred answers.

Property facts retain provenance: seller-provided, independently sourced, inferred, unknown or disputed. AI-generated listing content requires suitable review. Photograph interpretation cannot verify ownership, title, construction quality or surveyed boundaries.

Price research uses comparable advertised prices and applicable official indicators where available, never presenting listing prices as verified sales or its conclusions as certified valuations. Agricultural, industrial and investment findings are exploratory and do not replace professional assessments, permits or official planning decisions.

Persistent workflow states and audit logs protect against duplicate seller requests, unauthorized disclosure and double confirmation of appointments. Research and model failures must produce explicit uncertainty. Third-party data access and processing of personal information will follow applicable permissions and privacy safeguards.

### **References**

\[1\] National Association of REALTORS® (2025). [2025 Profile of Home Buyers and Sellers](https://cmr.realtor/clientuploads/2025_Profile_of_Home_Buyers_and_Sellers.pdf).

\[2\] Hebdzyński, M. (2023). [Quality information gaps in housing listings: Do words mean the same as pictures? Journal of Housing](https://doi.org/10.1007/s10901-023-10043-z) and the Built Environment.

\[3\] European Commission (2018). [Consumer market study on the functioning of real estate services in the European Union](https://www.uni-bremen.de/fileadmin/user_upload/fachbereiche/fb6/fb6/Forschung/ZERP/TENLAW/FollowUp/real_estate_services_summary_EU_en_october_2018.pdf).

\[4\] u/Embarrassed\_Bat\_2157 (2025), r/srilanka. [Sri Lankan sellers on online marketplaces](https://www.reddit.com/r/srilanka/comments/1hu66yw/). Includes the discussion shown in Figures 1–2.

\[5\] u/No\_Reading\_9586 (2026), r/srilanka. [How can I effectively market and sell land in Sri Lanka, especially to serious buyers or investors? Figure 3.](https://www.reddit.com/r/srilanka/comments/1qmi12i/how_can_i_effectively_market_and_sell_land_in_sri/)
