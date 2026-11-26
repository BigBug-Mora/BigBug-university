# Phase 1.1 · Runnable development foundation

Give a teammate one documented way to run the first Python service from a clean checkout and see it respond. This subphase establishes the repository entry point used by subsequent phases. [Phase 1](phase1.md) · [Repository layout](../repository-layout.md) · [Technology stack](../../mvp/teach-stack/tech-stack.md)

## Progress

- [x] Choose and record the Python version and dependency installation command. Put dependencies in their owning requirements files and pin the runtime versions used in the starter image.
- [x] Create the initial Property FastAPI package under `project/services/property/`, with a lightweight `GET /health` endpoint. Use `project/main.py` as a thin executable entry point that delegates to the app. Keep endpoint and startup concerns in focused files.
- [x] Add the initial Property Dockerfile and `project/compose.yaml` with the Property role. Document which configuration is needed for the starter and how to run it both directly and in Compose. Include a sample environment file only for configuration the starter uses.
- [x] Add a small service test and record the commands in the developer setup instructions. Update the repository layout if implementation changes any proposed paths.

## Acceptance check

Use the [developer setup commands](../../../README.md) from the repository root. Run the direct and Compose startups separately because both use port 8000. In each run, request `http://127.0.0.1:8000/health` and expect HTTP 200 with `{"status":"ok"}`. Run the service test without credentials.

## Verification and CI handoff

Verified on Windows on 2026-11-24 with Python 3.14.0, Docker Engine 29.6.1, and Docker Compose 5.3.0.

| Check | Command | Result |
| --- | --- | --- |
| Runtime dependencies | `python -m pip install -r project/requirements.txt` | Installed FastAPI 0.165.0 and Uvicorn 0.54.0 from the Property requirements. |
| Direct startup | `python project/main.py` | `GET /health` returned HTTP 200 and `{"status":"ok"}`. |
| Compose smoke test | `docker compose -f project/compose.yaml up --build --detach --wait` | Built `project/services/property/Dockerfile`, reached healthy, and returned the same response through the host port. Verified `docker compose -f project/compose.yaml down` afterward. |
| Service test | `python -m pip install -r project/services/property/tests/requirements.txt` followed by `python -m unittest discover -s project/services/property/tests -v` | One test passed. The Windows sandbox blocked asyncio's local socket setup, so the successful run used normal Windows networking. |

Rechecked on Windows on 2026-11-26. `python -m pip check` reported no broken requirements and the service test passed. The direct and Compose startups each returned HTTP 200 with `{"status":"ok"}` through the host port. The Compose service reached healthy and the test stack was removed afterward.

## Decision log

- Start with Property to establish the development and packaging pattern for listing work. Add the other service images when their phases need them.
- Use Python 3.14 for development and CI and `python:3.14.6-slim-bookworm` for the starter image. `project/requirements.txt` delegates to the Property runtime requirements. Keep HTTPX2 in the service's test requirements.
- Publish port 8000 on loopback for local development. `/health` reports process liveness and needs no configuration or external dependencies.
