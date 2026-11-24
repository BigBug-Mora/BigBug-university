# Agent Worker Container

[Container directory](../containers.md) · [Agent API](../agent-api/agent-api.md) · [MVP agent behavior](../../agent-details/agent-details.md)

## Runtime and inputs

Run the Celery worker from the shared Python agent image and receive jobs through RabbitMQ. Reuse the same Claude client, workflow definitions, output validation, and guardrails as Agent API. Run the workflow assigned to each authorized job.

Start with one `agent-worker` container per environment and configure Celery with two execution slots. Either slot can run an inspection or showcase job. Additional ready jobs wait for capacity.

| Job | Inputs and result | Reference |
| --- | --- | --- |
| Photo and draft inspection | Authorized draft revision and photo set. Returns grounded observations and optional improvement suggestions. | [Property Inspector Agent](property-inspector-agent.md) |
| Showcase creation or revision | Authorized publishable facts, photo choices, and relevant inspection findings. Returns an editable showcase draft. | [Property Showcase Creator Agent](property-showcase-creator-agent.md) |

## Job lifecycle

1. Receive a job ID from [RabbitMQ](../rabbitmq/rabbitmq.md). Load the durable job record and atomically claim it under the agreed concurrency policy. A completed job is safe to acknowledge after redelivery.
2. Confirm the job scope and obtain revision-specific inputs through [Property service](../property-service/property-service.md). Use authorized S3 access for required photos. Reject or supersede jobs whose required inputs are unavailable or whose revisions cannot be used safely.
3. Run the LangGraph workflow and validate the result. Use a bounded model timeout and retry policy. Separate transient failures such as a provider timeout from invalid or permanently unavailable inputs.
4. Save an inspection result against the inspected revision in durable workflow records. Send a validated showcase result to Property service as a draft with the job ID and input revision. Make resubmission safe if the property write succeeds but the worker stops before marking the job complete.
5. Persist the final state and acknowledge the delivery under the chosen policy. If interrupted or redelivered, recover using the durable job state and its stable result identity. Preserve the last valid listing and showcase during failures.

## Permissions, recovery, and operation

Use job-scoped access to files and data. Keep images, signed URLs, private details, and free-form model input out of broker messages and logs. Report job ID, revision, run outcome, duration, and retry count. Show actionable failure status through Agent API.

Configure concurrency against model limits, CPU and memory, and database capacity. Verify duplicate deliveries, an interrupted worker, stale inputs, broker outages, and a failed showcase write with a retry. Finalize claim recovery, retry and timeout limits, and environment isolation before enabling shared development workers.
