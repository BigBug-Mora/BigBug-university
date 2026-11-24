# Phase 1.1 · Runnable development foundation

Give a teammate one documented way to run the first Python service from a clean checkout and see it respond. This subphase establishes the repository entry point used by subsequent phases. [Phase 1](phase1.md) · [Repository layout](../repository-layout.md) · [Technology stack](../../mvp/teach-stack/tech-stack.md)

## Progress

- [ ] Choose and record the Python version and dependency installation command. Put dependencies in their owning requirements files and pin the runtime versions used in the starter image.
- [ ] Create the initial Property FastAPI package under `project/services/property/`, with a lightweight `GET /health` endpoint. Use `project/main.py` as a thin executable entry point that delegates to the app. Keep endpoint and startup concerns in focused files.
- [ ] Add the initial Property Dockerfile and `project/compose.yaml` with the Property role. Document which configuration is needed for the starter and how to run it both directly and in Compose. Include a sample environment file only for configuration the starter uses.
- [ ] Add a small service test and record the commands in the developer setup instructions. Update the repository layout if implementation changes any proposed paths.

## Acceptance check

From the root, start the app with the documented `project/main.py` command, then build and start it in Compose using `docker compose -f project/compose.yaml up --build`. In each run, request the documented local `/health` URL and expect HTTP 200 with the agreed response body. Run the service test without credentials. Record exact commands, actual paths, and the result for Phase 1.3.

## Decision log

- Start with Property to establish the development and packaging pattern for listing work. Add the other service images when their phases need them.
