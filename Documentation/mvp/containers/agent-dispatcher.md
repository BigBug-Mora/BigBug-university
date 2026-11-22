# Agent Dispatcher Container

[Container directory](containers.md) · [Agent API](agent-api/agent-api.md) · [RabbitMQ](rabbitmq.md) · [Agent worker](agent-worker/agent-worker.md)

## Runtime and responsibility

Run a dedicated dispatch process from the shared Python agent image using its own startup command. Agent API saves the background job and its pending dispatch record in one PostgreSQL transaction. The dispatcher publishes the saved request, and the worker runs the agent task.

## Dispatch flow

1. Read eligible unsent dispatch records from PostgreSQL.
2. Publish the Celery task message to RabbitMQ with the job ID. Check that the broker accepted the publish and routed it to a queue.
3. Mark the dispatch record sent after those checks. If publishing fails or the outcome is uncertain, leave it eligible for retry. A retry can publish the same job ID again, so the worker handles duplicate deliveries against the persisted job record.

The dispatcher can restart independently of Agent API. During a dispatcher outage, new job requests can still be saved. Pending records are eligible for dispatch when the process resumes. Track publish failures and the age of pending dispatch records. Confirm the environment ownership rule before dispatchers use the shared database.
