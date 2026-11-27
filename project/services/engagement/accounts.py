"""Resolve verified identities through Engagement's account store."""

from uuid import UUID, uuid4

import psycopg

from project.shared.cognito import VerifiedIdentity


class DisabledAccount(Exception):
    pass


class AccountStoreUnavailable(Exception):
    pass


class AccountStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def resolve(self, identity: VerifiedIdentity) -> UUID:
        identity_key = (identity.issuer, identity.subject)
        try:
            with psycopg.connect(self._database_url, connect_timeout=3, options="-c statement_timeout=5000") as db:
                db.isolation_level = psycopg.IsolationLevel.READ_COMMITTED
                row = db.execute(
                    """
                    INSERT INTO account.accounts (id, cognito_issuer, cognito_subject)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cognito_issuer, cognito_subject) DO NOTHING
                    RETURNING id, status
                    """,
                    (uuid4(), *identity_key),
                ).fetchone()
                if row is None:
                    # READ COMMITTED gives this statement a fresh snapshot after a conflicting insert.
                    row = db.execute(
                        """
                        SELECT id, status FROM account.accounts
                        WHERE cognito_issuer = %s AND cognito_subject = %s
                        """,
                        identity_key,
                    ).fetchone()
                if row is None:
                    raise AccountStoreUnavailable
                account_id, status = row
                if status != "active":
                    raise DisabledAccount
        except psycopg.Error:
            raise AccountStoreUnavailable from None

        return account_id
