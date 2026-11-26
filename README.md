# EstateFlow

## Run the Property service

From the repository root, create a virtual environment with Python 3.14 and activate it in your shell.

```sh
python -m venv .venv
```

In PowerShell, run `.venv\Scripts\Activate.ps1`. In Bash or Zsh, run `source .venv/bin/activate`.

```sh
python -m pip install -r project/requirements.txt
python project/main.py
```

From another terminal, request `http://127.0.0.1:8000/health`. The response is HTTP 200 with `{"status":"ok"}`.

```sh
curl -i http://127.0.0.1:8000/health
```

Use `curl.exe` in Windows PowerShell. The health endpoint checks that the process is running. It requires no environment variables, database, or cloud credentials.

## Run with Docker Compose

Stop the direct Python server with Ctrl+C before running Compose. Both publish port 8000 on loopback. With a running Linux Docker engine and Docker Compose, run these commands from the repository root.

```sh
docker compose -f project/compose.yaml up --build --detach --wait
curl -i http://127.0.0.1:8000/health
docker compose -f project/compose.yaml down
```

## Run the service test

With the virtual environment active and runtime dependencies installed, run these commands from the repository root.

```sh
python -m pip install -r project/services/property/tests/requirements.txt
python -m unittest discover -s project/services/property/tests
```

The test runs in-process and verifies the health status and response body.

## Verify the disposable database

From the repository root, activate the virtual environment and install `project/requirements.txt` as above. Start the PostgreSQL 17 test database with Docker Compose.

```sh
docker compose -p estateflow-db-test -f project/compose.test.yaml up -d --wait
```

Set the migration connection for this shell. These credentials belong to the disposable database on loopback.

```powershell
$env:ESTATEFLOW_DATABASE_URL = "postgresql+psycopg://estateflow_migrator:disposable-migration@127.0.0.1:55432/estateflow_test"
```

In Bash or Zsh, use `export` instead.

```sh
export ESTATEFLOW_DATABASE_URL="postgresql+psycopg://estateflow_migrator:disposable-migration@127.0.0.1:55432/estateflow_test"
```

Apply the schema, load the fictional listings, and check the results. The second upgrade should report no migration to run, and the final command should show `0001 (head)` for the initial schema.

```sh
python -m alembic -c project/alembic.ini upgrade head
docker compose -p estateflow-db-test -f project/compose.test.yaml exec -T db psql -X -U estateflow_migrator -d estateflow_test -v ON_ERROR_STOP=1 -f /fixtures/listings.sql
docker compose -p estateflow-db-test -f project/compose.test.yaml exec -T db psql -X -U estateflow_migrator -d estateflow_test -v ON_ERROR_STOP=1 -f /checks/assert_database.sql
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
```

Tear down the disposable project. Its database is stored in memory and resets when the container stops.

```sh
docker compose -p estateflow-db-test -f project/compose.test.yaml down
```
