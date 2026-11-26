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
