import os
from logging.config import dictConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"stderr": {"class": "logging.StreamHandler"}},
    "loggers": {
        "alembic": {"handlers": ["stderr"], "level": "INFO", "propagate": False},
    },
})


def run_migrations() -> None:
    if context.is_offline_mode():
        context.configure(dialect_name="postgresql")
        with context.begin_transaction():
            context.run_migrations()
        return

    database_url = os.environ.get("ESTATEFLOW_DATABASE_URL")
    if not database_url:
        raise SystemExit("Set ESTATEFLOW_DATABASE_URL to the migration owner's PostgreSQL URL.")

    url = make_url(database_url)
    if url.drivername != "postgresql+psycopg" or not url.host or not url.database:
        raise SystemExit("Use a postgresql+psycopg URL with an explicit host and database.")

    engine = create_engine(url, poolclass=NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
