"""Create the MVP schemas and seed required reference data."""

from pathlib import Path

from alembic import context, op


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    ddl = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")
    if context.is_offline_mode():
        context.get_context().impl.static_output(ddl)
        return

    # Psycopg supports multi-statement SQL when no parameters are bound.
    op.get_bind().exec_driver_sql(ddl, execution_options={"no_parameters": True})


def downgrade() -> None:
    raise NotImplementedError("The initial schema contains application data. Restore a backup to roll back.")
