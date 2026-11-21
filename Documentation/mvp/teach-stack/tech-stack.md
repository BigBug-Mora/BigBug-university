# EstateFlow AI MVP Technology Stack

The team will develop EstateFlow AI with **Next.js and FastAPI running on each teammate's computer** and **one shared AWS development environment for PostgreSQL, authentication, and file storage from day one**. This lets teammates work remotely against the same data while using their own machines for application compute. For the hosted demo, deploy both application runtimes to AWS along with the four-agent workflow they run.

The team has **one AWS Free Tier account with $100 in credits**. Treat these credits as a hard AWS budget and stay on the Free Plan. All four teammates have the **same AWS and shared development database access level**. Each teammate signs in with their own identity at that same access level. Buyer and seller permissions are separate application behavior and can be exercised with Cognito test accounts.

Use this document for the MVP's technology and deployment decisions and [MVP agent details](../agent-details/agent-details.md) for behavior and handoffs. In the table below, follow the **MVP approach** column for implementation. The **Proposal** column records the [original stack](../../complete%20scope/complete-scope.md#technology-stack). Application hosting on ECS with Fargate remains a candidate until the team confirms it.

## 1. Technology Stack

| Layer | Proposal | MVP approach |
| --- | --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS | Use this stack for seller onboarding, the inbox, listing pages, buyer search, and property chat. |
| Backend | Python, FastAPI, Docker, Docker Compose, domain-oriented microservices | Use one FastAPI application with modules for listings, photos, inquiries, approvals, and agent execution. Use Docker for repeatable packaging and Docker Compose where it helps run the application services together. |
| Agents and orchestration | LangGraph, LangChain, initially the Anthropic Claude API, with configurable provider integrations | Run the Seller Agent, Property Inspector Agent, Property Showcase Creator Agent, and Buyer Agent inside the backend. Start with **Claude Haiku 5.5** (`claude-haiku-5-5`) via the direct Anthropic Claude API for text and photo review. Use the same model for the single-agent benchmark. Use LangGraph for handoffs and LangChain integrations where they simplify model access. |
| Database and search | Amazon RDS for PostgreSQL, pgvector, and an embedding model | Use shared RDS PostgreSQL for application records. Start with structured listing filters and a pending-request rule based on the property and the underlying fact. Revisit embeddings and pgvector if evaluation shows a gap in search or question matching. |
| Files | Amazon S3 | Use shared S3 for listing photos and other files the application supports. Store object references in PostgreSQL and authorize file access through the backend. |
| Identity | Amazon Cognito with Auth.js and backend-enforced authorization | Use a shared Cognito user pool from day one. The proposal's Auth.js integration is the starting approach for Next.js. FastAPI verifies the authenticated identity and enforces ownership, inquiry access, and disclosure permissions. |
| Jobs and observability | RabbitMQ, Celery, GitHub Actions, OpenTelemetry, and structured logging | Persist workflow state and use structured logs for the MVP. Use GitHub Actions for routine checks as the team sets them up. Add a worker and queue if a workflow needs independent background execution. OpenTelemetry is available as a later observability option. |

The four AI roles share one backend deployment. The workflow coordinator runs their handoffs, and PostgreSQL is the application source of truth for listings, requests, approved facts, and disclosure grants.

Keep the runnable FastAPI entry point at `project/main.py` and Python dependencies at `project/requirements.txt`, as required by the [competition submission guide](../../Competition-Guidelines/University-Submission-Guide.md). Supporting backend modules can live under `project/`. The Next.js app lives in the same repository. Its exact directory and framework versions can be set when it is scaffolded.

**Application boundaries.** Next.js calls FastAPI for application data and actions. FastAPI derives the acting user from verified Cognito authentication and enforces access to each listing, inquiry, photo, and disclosure. Keep database credentials, Anthropic keys, and AWS credentials in server-side configuration. The frontend can receive an approved short-lived S3 URL for a specific upload or download. [Cognito token verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)

**Workflow state.** A buyer request and the seller's later answer are separate API actions. Save the pending request before returning to the buyer, and resume the workflow from PostgreSQL when the seller responds. LangGraph coordinates model steps. PostgreSQL enforces approval and pending-request rules, including preventing concurrent equivalent inquiries from creating duplicates.

## 2. Shared AWS Services From Day One

| AWS service | What it holds or does | How the team uses it |
| --- | --- | --- |
| **Amazon RDS for PostgreSQL** | Listings, property facts, inspection findings, showcase drafts, questions, approved answers, and permission grants | Every developer's local FastAPI instance uses the same private database. Start with one Single-AZ micro instance, subject to availability in the chosen region and account. |
| **Amazon Cognito** | Shared sign-in and test identities | Register localhost callbacks for development. Use separate buyer and seller test accounts to check what each identity can see or change. |
| **Amazon S3** | Shared listing photos and application uploads | Use a private development bucket. The API authorizes a file operation and can issue a short-lived signed URL for the permitted object. |

For private database access, the proposed development approach is **AWS Systems Manager Session Manager port forwarding** through a shared managed instance that can reach RDS. Each developer can authenticate and open a local tunnel for FastAPI. The browser uses the API for database-backed actions. [AWS remote host port forwarding](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html#sessions-remote-port-forwarding) · [Cognito callback URLs](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html) · [S3 signed URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

Use fictional or authorized test data in the shared development environment. Keep schema changes in versioned migrations and apply them explicitly as a team. Starting a local backend or running routine tests should leave the shared schema and records intact.

Check the account's remaining credits, plan end date, and service eligibility in the AWS console before provisioning. Budget for one RDS instance, one S3 bucket, one Cognito user pool, and any shared resource needed for private database access. Check the final hosting costs against the remaining balance before deploying. [AWS Free Tier plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) · [Amazon RDS Free Tier](https://aws.amazon.com/rds/free/)

Estimate AWS usage using resource sizes and runtime hours. Four users keep traffic small, while RDS and a managed tunnel instance can use credits even when nobody is testing. Reserve some credits for the hosted demo and delay deployment of the application servers until the final demo window.

## 3. Local Development and Offline Work

| Run or keep locally | How it works |
| --- | --- |
| **Next.js and FastAPI** | Each developer starts their own frontend and backend. The local frontend calls its local API. The API connects to the shared AWS services. |
| **Agents and workflow coordinator** | Prompts, routing, validation, and application logic execute inside local FastAPI. Live agent runs call the online model API. Use labeled fixtures or mocked model responses for routine development and offline tests. |
| **Fixtures and development tools** | Keep fictional listings, sample photos, test cases, build tools, and routine logs local. The offline fixture path uses test data and mock responses. Live integration tests use the shared AWS environment deliberately. |

`Local` describes where the code runs. A live local session still needs internet access for Cognito, RDS, S3, and the model API. An offline fixture test can exercise a screen or rule. The integration test should use the shared AWS environment.

**Model billing.** Both local and hosted backends call Anthropic directly. Claude API usage is billed separately from AWS and uses the team's Anthropic balance. Haiku 5.5 accepts text and images. Use the inspection fixtures to verify image-review quality before the benchmark. Use fixtures for routine UI work and record token use for live evaluation. [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview) · [Anthropic API pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Initial AWS smoke check.** From two laptops, verify Cognito sign-in, private database connectivity, and access to the same test photo in S3. Once the workflows are built, have one teammate publish a listing and the other find it and ask a question. Confirm the approved answer reaches the authorized buyer's original property chat.

## 4. Final AWS Deployment

For the hosted MVP, deploy the **Next.js frontend** and the **FastAPI backend** to AWS late in the build, with time to test the hosted URL before submission. The deployed backend carries all four agents and their workflow coordinator and connects to the **same RDS database and dataset, S3 bucket, and Cognito user pool** used during development. The hosted frontend provides the demo URL, and the backend continues to enforce access rules. Live agent inference still uses the direct Anthropic API. Local development and offline tests remain available after deployment.

**Proposed hosting option.** Package the frontend and backend as Docker images and run both applications on Amazon ECS with Fargate if the account plan supports the configuration and the remaining credits cover it. Confirm the hosting choice before provisioning. Use AWS-managed secrets for the deployed backend and register the hosted sign-in callback in Cognito. [Amazon ECS on Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) · [Secrets for ECS containers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html)

Before the demo, verify the same seller-to-buyer workflow from the hosted URL. Check sign-in, photo upload, listing search, question grouping, seller approval, answer delivery, and both agent handoffs. Keep developer fixtures and build tools in the development workflow.
