# EstateFlow repository layout

Use this map when adding files. Paths describe the intended layout as each phase lands. Create a folder when its first real file is needed. The [roadmap](roadmap.md) tracks build order and the [container design](../mvp/containers/containers.md) defines runtime ownership.

## Folder map

```text
AGENTS.md
.agents/
  AGENTS.md
Documentation/                 Team design references
  implementation/
    roadmap.md
    repository-layout.md
    phase-01/
      phase1.md
      phase1.1.md ... phase1.4.md
    phase-02/
      phase2.md
      phase2.1.md ... phase2.4.md
    phase-03/
      phase3.md
      phase3.1.md ... phase3.4.md
docs/                          Organizer materials
project/
  main.py                      Repository entry point
  requirements.txt             Python tooling and entry-point dependencies
  compose.yaml                 Local application services
  compose.test.yaml            Disposable integration dependencies
  alembic.ini                  Migration tooling configuration
  frontend/
  services/
    property/
    engagement/
    agent/
  shared/
  migrations/
  tests/
    fixtures/
    integration/
    e2e/
infra/
  aws/
  runbooks/
.github/
  workflows/
```

Keep the existing `project/main.py` as the documented entry point. Phase 1 defines its starter command and how it delegates to service processes. Pin image runtime dependencies from each image’s declared requirements or lockfile. If shared Python tooling requirements are needed, list them in `project/requirements.txt` and import them into image builds only when applicable. [MVP tooling and entry point](../mvp/teach-stack/tech-stack.md#1-technology-stack)

## Runtime roles and image boundaries

| Runtime role | Location and image | Process and ownership |
| --- | --- | --- |
| `frontend` | `project/frontend/Dockerfile` | Next.js server. Screens, session integration, and backend calls on behalf of the signed-in user. |
| `property-service` | `project/services/property/Dockerfile` | FastAPI. Verifies the actor for protected Property calls and owns listing revisions, facts, private detail values, photos, showcases, publication, and search. |
| `engagement-service` | `project/services/engagement/Dockerfile` | FastAPI. Owns account mapping, conversations, ordinary inquiries and deliveries, and private disclosure grants. |
| `agent-api` | `project/services/agent/Dockerfile` | FastAPI entry point. Runs interactive workflows and accepts jobs. |
| `agent-dispatcher` | Same Agent image | Dispatcher entry point. Reads dispatch records and publishes eligible jobs. |
| `agent-worker` | Same Agent image | Celery entry point. Claims and runs inspection and showcase jobs. |
| `rabbitmq` | RabbitMQ image configured in Compose and hosted infrastructure | Routes background jobs and holds queued messages. Pin the image version when implementing jobs. |

Keep Agent API, dispatcher, and worker entry points in separate modules inside the Agent service. Put workflows, provider adapters, and job state beside those entry points as they appear. The three processes share the image and relevant code. If a Python image needs `project/shared/`, build from the common `project/` context using its own Dockerfile and copy the service plus its declared shared dependencies. Verify the same entry points locally and in the hosted configuration. [Container design](../mvp/containers/containers.md) · [Worker design](../mvp/containers/agent-worker/agent-worker.md)

## Code placement and ownership

- Give each file a purpose you can describe in a sentence. Split a growing module along responsibilities such as HTTP input, publication rules, and database reads. Keep related code together while the responsibility is small.
- Keep service code and tests under its own folder. Within Property, for example, put publication and photos in separate modules when each has enough behavior to justify it.
- Put genuinely reused middleware, configuration helpers, or client primitives in `project/shared/`. Keep domain rules and models with their owning service. Agents use the owning API. For **Share answer**, implement the documented exception as a narrow Property-owned operation on the same database connection as Engagement. [Database ownership and transaction rules](../mvp/database/contracts.md)
- Maintain one ordered migration history in `project/migrations/` for shared PostgreSQL. Let the owning service review changes to its schema. Use a migration identity and separate runtime permissions. Apply shared-environment migrations explicitly. [Database schema](../mvp/database/schema.md) · [CI migration policy](../mvp/ci/cd/ci.md)
- Keep disposable fixtures and cross-service tests under `project/tests/`. Store the committed workflow in `.github/workflows/`. Keep AWS configuration in `infra/aws/` and human-run setup and deployment steps in `infra/runbooks/`. [Development and deployment](../mvp/teach-stack/tech-stack.md)

Record changes to this map in the phase that introduces them and update the map when those paths become the repository convention.
