import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import time
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from project.services.engagement.accounts import AccountStore
from project.services.engagement.app import build_app
from project.services.engagement.tests.identity_fixture import CLIENT_ID, IdentityFixture
from project.shared.cognito import CognitoVerifier
from project.shared.service_auth import SERVICE_TOKEN_HEADER, ServiceAuthenticator


RESOLVE = "/internal/accounts/resolve"
FRONTEND = "fixture-frontend-to-engagement"
PROPERTY = "fixture-property-to-engagement"
OTHER = "fixture-other-to-engagement"


class AccountResolutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime_url = os.environ["ESTATEFLOW_TEST_ENGAGEMENT_DATABASE_URL"]
        cls.owner_url = os.environ["ESTATEFLOW_TEST_MIGRATOR_DATABASE_URL"]
        cls.identities = cls.enterClassContext(IdentityFixture())

    def setUp(self):
        self.buyer = f"buyer-{uuid4()}"
        self.seller = f"seller-{uuid4()}"
        self.identities.published = "initial"
        self.identities.available = True
        self.identities.requests.clear()
        self.issuer = self.identities.issuer
        self.client = self.enterContext(self.make_client())
        self.addCleanup(self.remove_accounts)

    def make_client(self, *, issuer=None, runtime_url=None):
        verifier = CognitoVerifier(issuer or self.issuer, CLIENT_ID, allow_insecure_http=True)
        store = AccountStore(runtime_url or self.runtime_url)
        auth = ServiceAuthenticator({"frontend": FRONTEND, "property": PROPERTY, "other": OTHER})
        return TestClient(build_app(store, verifier, auth, {"frontend", "property"}))

    def resolve(self, token, *, caller=FRONTEND, client=None):
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        if caller is not None:
            headers[SERVICE_TOKEN_HEADER] = caller
        response = (client or self.client).post(RESOLVE, headers=headers)
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")
        return response

    def account_id(self, response):
        self.assertEqual(response.status_code, 200, response.text)
        return UUID(response.json()["account_id"])

    def accounts(self):
        with psycopg.connect(self.owner_url) as db:
            return db.execute(
                """
                SELECT id, cognito_issuer, cognito_subject, status
                FROM account.accounts WHERE cognito_subject IN (%s, %s)
                """,
                (self.buyer, self.seller),
            ).fetchall()

    def remove_accounts(self):
        with psycopg.connect(self.owner_url) as db:
            db.execute(
                "DELETE FROM account.accounts WHERE cognito_subject IN (%s, %s)",
                (self.buyer, self.seller),
            )

    def test_concurrent_first_use_and_retry_commit_one_account(self):
        token = self.identities.token(self.buyer)
        barrier = Barrier(8, timeout=10)

        def resolve_concurrently(index):
            barrier.wait()
            return self.account_id(self.resolve(token, caller=(FRONTEND, PROPERTY)[index % 2]))

        with ThreadPoolExecutor(max_workers=8) as threads:
            ids = set(threads.map(resolve_concurrently, range(8)))

        returning = self.account_id(self.resolve(self.identities.token(self.buyer, nbf=int(time()) - 1)))
        self.assertEqual(ids, {returning})
        self.assertEqual(self.accounts(), [(returning, self.issuer, self.buyer, "active")])
        self.assertEqual(self.identities.requests, ["/pool/.well-known/jwks.json"])
        with psycopg.connect(self.owner_url) as db:
            self.assertIsNone(db.execute("SELECT 1 FROM account.profiles WHERE account_id = %s", (returning,)).fetchone())

    def test_subject_and_issuer_both_distinguish_accounts(self):
        buyer = self.account_id(self.resolve(self.identities.token(self.buyer)))
        seller = self.account_id(self.resolve(self.identities.token(self.seller)))
        second_issuer = f"{self.issuer}-other"
        second_token = self.identities.token(self.buyer, iss=second_issuer)
        self.assertEqual(self.resolve(second_token).status_code, 401)
        with self.make_client(issuer=second_issuer) as second_client:
            other_buyer = self.account_id(self.resolve(second_token, client=second_client))
        self.assertEqual(len({buyer, seller, other_buyer}), 3)
        self.assertEqual(len(self.accounts()), 3)

    def test_caller_checked_before_bearer_verification(self):
        token = self.identities.token(self.buyer)
        for caller, status in ((None, 401), ("incorrect", 401), (OTHER, 403)):
            with self.subTest(status=status, caller=caller):
                self.assertEqual(self.resolve(token, caller=caller).status_code, status)
        self.assertEqual(self.identities.requests, [])
        self.assertEqual(self.accounts(), [])

    def test_rejected_bearer_credentials_create_no_account(self):
        now = int(time())
        for label, token in {
            "missing": None,
            "malformed": "malformed",
            "expired": self.identities.token(self.buyer, exp=now - 1),
            "missing expiration": self.identities.token(self.buyer, omit=("exp",)),
            "invalid expiration": self.identities.token(self.buyer, exp=str(now + 60)),
            "future nbf": self.identities.token(self.buyer, nbf=now + 60),
            "wrong issuer": self.identities.token(self.buyer, iss=f"{self.issuer}/different"),
            "wrong client": self.identities.token(self.buyer, client_id="another-client"),
            "wrong token type": self.identities.token(self.buyer, token_use="id"),
            "invalid signature": self.identities.token(self.buyer, signing_key="unpublished"),
            "empty subject": self.identities.token(""),
            "unknown signing key": self.identities.token(self.buyer, kid="unpublished"),
        }.items():
            with self.subTest(case=label):
                response = self.resolve(token)
                self.assertEqual(response.status_code, 401, response.text)
                self.assertEqual(response.json(), {"detail": "Unauthorized"})
        self.assertEqual(self.accounts(), [])

    def test_key_rotation_refreshes_cached_jwks(self):
        first = self.account_id(self.resolve(self.identities.token(self.buyer)))
        self.identities.published = "rotated"
        self.assertEqual(first, self.account_id(self.resolve(self.identities.token(self.buyer))))
        self.assertEqual(len(self.identities.requests), 2)

    def test_key_lookup_failure_denies_without_usable_cache(self):
        self.identities.available = False
        response = self.resolve(self.identities.token(self.buyer))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})
        self.assertEqual(self.accounts(), [])

    def test_account_is_checked_again_after_disabling(self):
        token = self.identities.token(self.buyer)
        account_id = self.account_id(self.resolve(token))
        with psycopg.connect(self.owner_url) as db:
            db.execute("UPDATE account.accounts SET status = 'disabled' WHERE id = %s", (account_id,))
        self.assertEqual(self.resolve(token).status_code, 403)
        self.assertEqual(self.accounts(), [(account_id, self.issuer, self.buyer, "disabled")])

    def test_unavailable_database_returns_503(self):
        url = psycopg.conninfo.make_conninfo(self.runtime_url, dbname=f"missing_{uuid4().hex}")
        with self.make_client(runtime_url=url) as unavailable:
            response = self.resolve(self.identities.token(self.buyer), client=unavailable)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})
        self.assertEqual(self.accounts(), [])

    def test_runtime_grants_limit_schema_and_table_access(self):
        for statement in (
            "CREATE SCHEMA prohibited_runtime_probe",
            "CREATE TABLE account.prohibited_runtime_probe (id int)",
            "SELECT 1 FROM property.listings",
            "SELECT 1 FROM account.profiles",
            "UPDATE account.accounts SET status = 'active'",
            "DELETE FROM account.accounts",
        ):
            with self.subTest(statement=statement):
                with psycopg.connect(self.runtime_url) as db:
                    with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                        db.execute(statement)
