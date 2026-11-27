import json
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from time import time
from uuid import uuid4

from fastapi.testclient import TestClient

from project.services.property.actor import ActorAuthentication
from project.services.property.app import build_app
from project.services.property.engagement import EngagementResolver
from project.shared.cognito import CognitoVerifier
from project.shared.service_auth import SERVICE_TOKEN_HEADER, ServiceAuthenticator
from project.tests.fixtures.identity_provider import CLIENT_ID, IdentityFixture


IDENTITY = "/internal/identity/me"
FRONTEND = "fixture-frontend-to-property"
PROPERTY = "fixture-property-to-engagement"
OTHER = "fixture-other-to-property"


class IdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identities = cls.enterClassContext(IdentityFixture())

    def setUp(self):
        self.calls = []
        self.result = (200, {"account_id": str(uuid4())})
        self.identities.requests.clear()
        self.identities.available = True
        self.addCleanup(setattr, self.identities, "available", True)
        self.resolver = self.start_resolver()
        self.client = self.enterContext(TestClient(self.app(self.resolver)))

    def start_resolver(self):
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                fixture.calls.append((
                    self.path,
                    self.headers["Authorization"],
                    self.headers[SERVICE_TOKEN_HEADER],
                ))
                status, payload = fixture.result
                data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Location", "/unexpected-redirect")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.addCleanup(server.server_close)
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        return EngagementResolver(f"http://127.0.0.1:{server.server_port}", PROPERTY)

    def app(self, resolver):
        return build_app(ActorAuthentication(
            CognitoVerifier(self.identities.issuer, CLIENT_ID, allow_insecure_http=True),
            ServiceAuthenticator({"frontend": FRONTEND, "other": OTHER}),
            resolver,
        ))

    def request(self, token=None, caller=FRONTEND, *, extra=(), client=None):
        headers = list(extra)
        if caller is not None:
            headers.append((SERVICE_TOKEN_HEADER, caller))
        if token is not None:
            headers.append(("Authorization", f"Bearer {token}"))
        response = (client or self.client).get(IDENTITY, headers=headers)
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")
        return response

    def test_verified_request_forwards_original_token_and_scoped_credential(self):
        token = self.identities.token("buyer")
        response = self.request(token, extra=[
            ("X-EstateFlow-Account-Id", str(uuid4())),
            ("X-EstateFlow-Caller", "other"),
        ])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.result[1])
        self.assertEqual(self.calls, [("/internal/accounts/resolve", f"Bearer {token}", PROPERTY)])

    def test_denies_missing_wrong_and_disallowed_callers_before_verifying(self):
        token = self.identities.token("buyer")
        for caller, status in ((None, 401), ("wrong", 401), (PROPERTY, 401), (OTHER, 403)):
            with self.subTest(caller=caller):
                self.assertEqual(self.request(token, caller=caller).status_code, status)
        self.assertEqual(self.request(token, extra=[(SERVICE_TOKEN_HEADER, FRONTEND)]).status_code, 401)
        self.assertEqual(self.identities.requests, [])
        self.assertEqual(self.calls, [])

    def test_denies_missing_and_unverified_bearers_before_resolving(self):
        for token in (
            None,
            "malformed",
            self.identities.token("buyer", exp=int(time()) - 1),
            self.identities.token("buyer", client_id="other-client"),
            self.identities.token("buyer", signing_key="unpublished"),
        ):
            with self.subTest(status=401):
                response = self.request(token, extra=[("X-EstateFlow-Account-Id", str(uuid4()))])
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json(), {"detail": "Unauthorized"})
        token = self.identities.token("buyer")
        self.assertEqual(self.request(token, extra=[("Authorization", f"Bearer {token}")]).status_code, 401)
        self.assertEqual(self.calls, [])

    def test_rechecks_disabled_account_after_success(self):
        token = self.identities.token("buyer")
        self.assertEqual(self.request(token).status_code, 200)
        self.result = (403, {"detail": "Forbidden"})
        response = self.request(token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Forbidden"})
        self.assertEqual(len(self.calls), 2)

    def test_resolver_failures_return_generic_503_without_redirecting(self):
        token = self.identities.token("buyer")
        for result in (
            (503, {}), (401, {}), (307, {}), (200, b"not JSON"), (200, b"x" * 4097),
            (200, []), (200, {}), (200, {"account_id": "bad UUID"}),
        ):
            with self.subTest(status=result[0]):
                self.result = result
                response = self.request(token)
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json(), {"detail": "Service unavailable"})
        self.assertEqual(len(self.calls), 8)

    def test_jwks_failure_does_not_call_resolver(self):
        self.identities.available = False
        response = self.request(self.identities.token("buyer"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.calls, [])
