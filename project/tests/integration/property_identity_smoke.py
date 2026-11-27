"""Exercise the Compose Property and Engagement images with disposable fixtures."""

import json
import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

import psycopg

from project.shared.service_auth import SERVICE_TOKEN_HEADER
from project.tests.fixtures.identity_provider import IdentityFixture


PROPERTY = "http://property-service:8000/internal/identity/me"
ENGAGEMENT = "http://engagement-service:8000/internal/accounts/resolve"
DISPOSABLE_DB = "postgresql://estateflow_migrator:disposable-migration@db:5432/estateflow_test"


class PropertyIdentitySmokeTest(unittest.TestCase):
    def setUp(self):
        self.identities = self.enterContext(IdentityFixture(
            "0.0.0.0", 47122, issuer_host="identity-fixture"
        ))
        self.subjects = [f"{role}-{uuid4()}" for role in ("buyer", "seller")]
        self.property_secret = os.environ["ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN"]
        self.engagement_secret = os.environ["ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN"]
        self.addCleanup(self.remove_accounts)

    def remove_accounts(self):
        with psycopg.connect(DISPOSABLE_DB) as db:
            db.execute("DELETE FROM account.accounts WHERE cognito_subject = ANY(%s)", (self.subjects,))

    def call(self, url, method, token, secret, expected_status):
        request = Request(url, method=method)
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        if secret:
            request.add_header(SERVICE_TOKEN_HEADER, secret)
        try:
            response = urlopen(request, timeout=8)
        except HTTPError as error:
            response = error
        with response:
            self.assertEqual(response.status, expected_status)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            return json.load(response)

    def test_account_identity_and_status_across_containers(self):
        buyer, seller = (self.identities.token(subject) for subject in self.subjects)
        for token, secret in ((buyer, None), (buyer, self.engagement_secret), (None, self.property_secret)):
            with self.subTest(token_present=bool(token), secret_present=bool(secret)):
                denied = self.call(PROPERTY, "GET", token, secret, 401)
                self.assertEqual(denied, {"detail": "Unauthorized"})

        accounts = []
        for token in (buyer, seller):
            expected = self.call(ENGAGEMENT, "POST", token, self.engagement_secret, 200)
            actual = self.call(PROPERTY, "GET", token, self.property_secret, 200)
            self.assertEqual(actual, expected)
            accounts.append(UUID(actual["account_id"]))
        self.assertNotEqual(*accounts)

        with psycopg.connect(DISPOSABLE_DB) as db:
            db.execute("UPDATE account.accounts SET status = 'disabled' WHERE id = %s", (accounts[0],))
        denied = self.call(PROPERTY, "GET", buyer, self.property_secret, 403)
        self.assertEqual(denied, {"detail": "Forbidden"})
        self.assertEqual(
            self.call(PROPERTY, "GET", seller, self.property_secret, 200),
            {"account_id": str(accounts[1])},
        )
