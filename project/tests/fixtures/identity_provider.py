"""Serve local JWKS and sign fictional Cognito-shaped access tokens."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from time import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


CLIENT_ID = "estateflow-test-client"


class IdentityFixture:
    def __init__(
        self, bind_host: str = "127.0.0.1", bind_port: int = 0, *, issuer_host: str = "127.0.0.1"
    ) -> None:
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.issuer_host = issuer_host
        self.keys = {
            kid: rsa.generate_private_key(public_exponent=65537, key_size=2048)
            for kid in ("initial", "rotated", "unpublished")
        }
        self.published = "initial"
        self.available = True
        self.requests = []

    def __enter__(self):
        fixture = self

        class JwksHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                fixture.requests.append(self.path)
                if not fixture.available:
                    self.send_error(503)
                    return
                key = fixture.keys[fixture.published].public_key()
                jwk = RSAAlgorithm.to_jwk(key, as_dict=True)
                jwk.update(kid=fixture.published, alg="RS256", use="sig")
                data = json.dumps({"keys": [jwk]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer((self.bind_host, self.bind_port), JwksHandler)
        self.thread = Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.issuer = f"http://{self.issuer_host}:{self.server.server_port}/pool"
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def token(self, subject, *, kid=None, signing_key=None, omit=(), **overrides):
        kid = kid or self.published
        claims = {
            "iss": self.issuer,
            "sub": subject,
            "client_id": CLIENT_ID,
            "token_use": "access",
            "exp": int(time()) + 120,
        }
        claims.update(overrides)
        for claim in omit:
            del claims[claim]
        return jwt.encode(claims, self.keys[signing_key or kid], algorithm="RS256", headers={"kid": kid})
