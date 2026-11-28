"""Run frontend, identity, draft and publication acceptance on a disposable stack."""

import os
from pathlib import Path
import subprocess
import sys
from time import monotonic, sleep
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[3]
FRONTEND = ROOT / "project/frontend"
COMPOSE = [
    "docker", "compose", "-p", "estateflow-identity-test",
    "-f", "project/compose.yaml", "-f", "project/compose.test.yaml",
    "-f", "project/compose.identity-test.yaml", "--profile", "identity",
]
MIGRATOR = "postgresql://estateflow_migrator:disposable-migration@127.0.0.1:55432/estateflow_test"
RUNTIME = "postgresql://estateflow_engagement:disposable-engagement"
TEST_SETTINGS = {
    "AUTH_URL": "http://127.0.0.1:3000",
    "AUTH_SECRET": "estateflow-local-playwright-session-secret-never-for-hosting",
    "ESTATEFLOW_TEST_IDENTITY_STACK": "1",
    "ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER": "1",
    "ESTATEFLOW_COGNITO_ISSUER": "http://identity-fixture:47121",
    "ESTATEFLOW_COGNITO_LOGIN_ORIGIN": "http://identity-fixture:47121",
    "ESTATEFLOW_COGNITO_CLIENT_ID": "estateflow-fixture-client",
    "ESTATEFLOW_COGNITO_CLIENT_SECRET": "estateflow-fixture-client-secret",
    "ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN": "estateflow-fixture-frontend-token",
    "ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN": "estateflow-fixture-frontend-to-property-token",
    "ESTATEFLOW_PROPERTY_TO_ENGAGEMENT_TOKEN": "estateflow-fixture-property-to-engagement-token",
    "ESTATEFLOW_ENGAGEMENT_BASE_URL": "http://engagement-service:8000",
    "ESTATEFLOW_ENGAGEMENT_DATABASE_URL": f"{RUNTIME}@db:5432/estateflow_test",
    "ESTATEFLOW_TEST_ENGAGEMENT_DATABASE_URL": f"{RUNTIME}@127.0.0.1:55432/estateflow_test",
    "ESTATEFLOW_TEST_MIGRATOR_DATABASE_URL": MIGRATOR,
    "ESTATEFLOW_TEST_PROPERTY_DATABASE_URL": "postgresql://estateflow_property:disposable-property@127.0.0.1:55432/estateflow_test",
    "ESTATEFLOW_DATABASE_URL": MIGRATOR.replace("postgresql:", "postgresql+psycopg:", 1),
}


def run(*args, cwd=ROOT, stdin=None, check=True, timeout=120, environment=None):
    return subprocess.run(
        args, cwd=cwd, env=os.environ | TEST_SETTINGS | (environment or {}),
        stdin=stdin, check=check, timeout=timeout,
    )


def psql(user, *args, script=None):
    command = [*COMPOSE, "exec", "-T", "db", "psql", "-X", "-U", user,
               "-d", "estateflow_test", "-v", "ON_ERROR_STOP=1"]
    if script:
        with (ROOT / "infra/aws" / script).open("rb") as sql:
            run(*command, *args, stdin=sql)
    else:
        run(*command, *args)


def wait_for_frontend():
    deadline = monotonic() + 30
    while monotonic() < deadline:
        try:
            with urlopen(f"{TEST_SETTINGS['AUTH_URL']}/", timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            sleep(1)
    raise RuntimeError("Frontend did not become ready.")


def main():
    python = sys.executable
    npm = ("cmd.exe", "/d", "/c", "npm.cmd") if os.name == "nt" else ("npm",)
    try:
        run(*COMPOSE, "down", "--timeout", "5")
        for script in ("lint", "build", "typecheck", "test:e2e"):
            run(*npm, "run", script, cwd=FRONTEND, timeout=180,
                environment={"ESTATEFLOW_TEST_IDENTITY_STACK": "0", "NEXT_TELEMETRY_DISABLED": "1"})
        run(*COMPOSE, "up", "-d", "--wait", "db")
        run(python, "-m", "alembic", "-c", "project/alembic.ini", "upgrade", "head")
        psql("postgres", script="provision-engagement-runtime.sql")
        psql("postgres",
             "-c", "ALTER ROLE estateflow_engagement PASSWORD 'disposable-engagement'",
             "-c", "REVOKE CONNECT, TEMPORARY ON DATABASE estateflow_test FROM PUBLIC")
        psql("estateflow_migrator", script="grant-engagement-runtime.sql")
        psql("postgres", script="provision-property-runtime.sql")
        psql("postgres", "-c", "ALTER ROLE estateflow_property PASSWORD 'disposable-property'")
        psql("estateflow_migrator", script="grant-property-runtime.sql")
        psql("estateflow_migrator", "-f", "/fixtures/listings.sql", "-f", "/checks/assert_database.sql")
        run(python, "-m", "alembic", "-c", "project/alembic.ini", "upgrade", "head")
        run(python, "-m", "alembic", "-c", "project/alembic.ini", "current", "--check-heads")
        for service in ("property", "engagement"):
            run(python, "-W", "error::ResourceWarning", "-m", "unittest", "discover",
                "-s", f"project/services/{service}/tests", "-v")
        run(*COMPOSE, "up", "--build", "-d", "--wait", timeout=600)
        wait_for_frontend()
        run(*npm, "run", "test:e2e", cwd=FRONTEND, timeout=240)
    except Exception:
        run(*COMPOSE, "logs", "--no-color", "--tail", "80", check=False, timeout=20)
        raise
    finally:
        run(*COMPOSE, "down", "--timeout", "5", timeout=30)


if __name__ == "__main__":
    main()
