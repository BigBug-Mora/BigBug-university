# Agent API Container

[Container directory](../containers.md) · [MVP agent behavior](../../agent-details/agent-details.md)

## Runtime and responsibilities

Run the interactive Python FastAPI process. Use LangGraph to coordinate agent steps and the shared Anthropic client to call Claude directly. Use SQLAlchemy for application-owned run, job, and dispatch records in PostgreSQL. The [Agent worker](../agent-worker/agent-worker.md) shares the workflow code, model client, structured output definitions, and guardrail code through the same image.

| Workflow | Entry point | Reference |
| --- | --- | --- |
| Buyer Agent | Live search or property-chat turn. | [Buyer Agent](buyer-agent.md) |
| Seller Agent | Live listing preparation, improvements, and inquiry responses. | [Seller Agent](seller-agent.md) |
| Property Inspector | Accept an authorized job against a draft revision. | [Property Inspector](../agent-worker/property-inspector-agent.md) |
| Property Showcase Creator | Accept an authorized job for a draft or showcase revision. | [Property Showcase Creator](../agent-worker/property-showcase-creator-agent.md) |

## Interactive execution

1. Validate the action and actor. Resolve the conversation or draft and its scope through the owning service.
2. Load only the relevant permitted facts and messages. For property chat, [Engagement service](../engagement-service.md) owns the transcript. Agent API selects the context for each turn and obtains listing facts from [Property service](../property-service.md).
3. Run the appropriate LangGraph workflow with bounded time and model calls. Give it typed tool inputs and the least data and permissions necessary. Bind listing tools to the active listing during Property Chat.
4. Check the output shape, fact support, qualifiers, and visibility before returning it or passing it to an owning service. If the evidence is missing or conflicting, follow the relevant workflow's unknown or clarification path.
5. Persist the completed reply through the owning service when the workflow has a transcript. Return the saved reply and state. Use a stable turn identifier to recover from a retry or a disconnect after a reply was saved.

## Background job acceptance

Verify the seller's authority and resolve the input revision through Property service. Save the job and its pending dispatch record in one transaction. Return a durable job ID and an accepted state after the transaction commits. The [Agent dispatcher](../agent-dispatcher.md) publishes the task to RabbitMQ. Scope job status and results to the requesting actor and authorized listing. A broker outage may delay work while the durable pending job remains visible.

## Guardrails and operations

- Treat chat text, listings, seller replies, and media as untrusted model inputs. Bind allowed operations to the workflow in code. Model output can propose a change or display a confirmation action. A domain service enforces the explicit user approval before committing it.
- Keep exact addresses, raw coordinates, phone numbers, and credentials out of ordinary model context and traces. A protected result is resolved through a separate backend operation after the grant is checked.
- Record safe identifiers, run outcome, provider latency, and model usage. Report dependency errors without exposing inputs, inaccessible records, or credentials.
- Verify separate property scope, a missing-fact response, a retried chat turn, malformed model output, and durable job acceptance during a broker outage. Finalize turn delivery and service authentication before implementing those contracts.
