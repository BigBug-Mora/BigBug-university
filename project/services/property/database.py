import os
from contextlib import contextmanager

import psycopg
from fastapi import HTTPException
from psycopg.rows import dict_row


@contextmanager
def transaction():
    url = os.environ.get("ESTATEFLOW_PROPERTY_DATABASE_URL")
    if not url:
        raise HTTPException(503, "Draft store unavailable")
    try:
        with psycopg.connect(
            url, row_factory=dict_row, connect_timeout=3, options="-c statement_timeout=5000"
        ) as db:
            yield db
    except (psycopg.errors.CheckViolation, psycopg.DataError):
        raise HTTPException(
            422, "Check the fields, related counts, price and measurement units."
        ) from None
    except psycopg.Error:
        raise HTTPException(503, "Draft store unavailable") from None


def owned_listing(db, listing, seller, *, lock=False):
    query = """SELECT id, current_draft_revision_id, current_showcase_id FROM property.listings
               WHERE id = %s AND seller_account_id = %s"""
    row = db.execute(query + (" FOR UPDATE" if lock else ""), (listing, seller)).fetchone()
    if row is None:
        raise HTTPException(404, "Listing unavailable")
    return row
