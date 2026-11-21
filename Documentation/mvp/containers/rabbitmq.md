# RabbitMQ Container

[Container directory](containers.md) · [Agent API](agent-api/agent-api.md) · [Agent worker](agent-worker/agent-worker.md)

## Runtime and responsibility

Run the RabbitMQ message broker in the proposed background-job setup. It routes job messages from the authorized publisher to the Celery worker and tracks delivery and acknowledgement. The application keeps job state and results in PostgreSQL. Job status shown in the frontend comes from Agent API.

## Message lifecycle

1. A seller action creates a durable job and a dispatch record in one database transaction. The dispatch process publishes a persistent job message to a durable route and checks broker confirmation and routing before marking the dispatch complete.
2. The broker delivers the job ID to a worker with available capacity. The worker retrieves the authorized inputs using the durable job record.
3. The worker stores the result or a terminal outcome and acknowledges according to the job policy. A crash before acknowledgement can cause redelivery. A lost publisher confirmation can also lead to repeated publication. The worker must handle the same job ID safely in either case.

Use small messages with job identifiers and any agreed routing metadata. Keep files in S3 and all authoritative job and business state in PostgreSQL. Use bounded retries and choose how terminal failures are surfaced and replayed. Keep queued messages across broker restarts using persistent storage in the selected deployment.

## Access and environment isolation

Keep broker access private. Give the dispatcher and worker the permissions needed for their roles. Keep broker credentials in server-side configuration. Restrict any management interface to authorized operators. Set appropriate limits for job timeouts, worker prefetch, queue growth, and alerting on backlogs and stuck dispatches.

With a local broker per laptop and shared RDS, a local dispatcher and worker need a reliable way to identify the jobs they own. Hosted dispatch and consumption require the same separation from development traffic. Define the environment ownership and routing rule before implementing the outbox query or starting shared-data workers.

Test an outage before publish, a broker restart while jobs are pending, interruption before acknowledgement, duplicate publication, and isolation across two local environments. Finalize dispatcher placement, queue and failure routing, and the hosted broker lifecycle with the application deployment plan.
