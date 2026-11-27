"""Verify Cognito access tokens against a configured user pool."""

import json
from dataclasses import dataclass
from http.client import HTTPException
from threading import Lock
from time import monotonic
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener

import jwt


class InvalidAccessToken(Exception):
    pass


class VerificationUnavailable(Exception):
    pass


@dataclass(frozen=True)
class VerifiedIdentity:
    issuer: str
    subject: str


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class CognitoVerifier:
    _cache_seconds = 300
    _refresh_interval = 5
    _request_timeout = 2
    _max_jwks_bytes = 64 * 1024

    def __init__(self, issuer: str, client_id: str, *, allow_insecure_http: bool = False) -> None:
        url = urlsplit(issuer)
        allowed_schemes = ("https", "http") if allow_insecure_http else ("https",)
        if (
            url.scheme not in allowed_schemes
            or not url.hostname
            or url.username is not None
            or url.query
            or url.fragment
            or issuer.endswith("/")
            or not client_id
        ):
            raise ValueError("Configure a Cognito issuer URL and app client ID.")
        self._issuer = issuer
        self._client_id = client_id
        self._jwks_url = f"{issuer}/.well-known/jwks.json"
        self._opener = build_opener(_NoRedirects())
        self._lock = Lock()
        self._keys: dict[str, jwt.PyJWK] = {}
        self._expires_at = 0.0
        self._next_refresh_at = 0.0
        self._refresh_failed = False

    def verify_bearer(self, authorization: str | None) -> VerifiedIdentity:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() != "bearer" or not token or len(token) > 8192:
            raise InvalidAccessToken

        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if header.get("alg") != "RS256" or not isinstance(kid, str) or not kid:
                raise InvalidAccessToken
            key = self._signing_key(kid)
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={"require": ["iss", "sub", "exp"], "verify_aud": False},
            )
        except (jwt.InvalidTokenError, TypeError, ValueError, OverflowError, RecursionError):
            raise InvalidAccessToken from None

        subject = claims["sub"]
        if (
            claims.get("token_use") != "access"
            or claims.get("client_id") != self._client_id
            or not isinstance(subject, str)
            or not subject.strip()
            or "\x00" in subject
            or type(claims["exp"]) is not int
            or ("nbf" in claims and type(claims["nbf"]) is not int)
        ):
            raise InvalidAccessToken
        try:
            subject.encode("utf-8")
        except UnicodeEncodeError:
            raise InvalidAccessToken from None
        return VerifiedIdentity(self._issuer, subject)

    def _signing_key(self, kid: str) -> jwt.PyJWK:
        with self._lock:
            now = monotonic()
            if now < self._expires_at and kid in self._keys:
                return self._keys[kid]

            # Limit network requests for unknown key IDs across concurrent callers.
            if now >= self._next_refresh_at:
                cold_start = not self._keys
                try:
                    self._keys = self._fetch_keys()
                except (OSError, HTTPException, ValueError, TypeError, RecursionError, jwt.PyJWTError):
                    self._refresh_failed = True
                else:
                    self._refresh_failed = False
                    self._expires_at = monotonic() + self._cache_seconds
                if not cold_start or self._refresh_failed or kid not in self._keys:
                    self._next_refresh_at = monotonic() + self._refresh_interval

            if self._refresh_failed or monotonic() >= self._expires_at:
                raise VerificationUnavailable
            if kid not in self._keys:
                raise InvalidAccessToken
            return self._keys[kid]

    def _fetch_keys(self) -> dict[str, jwt.PyJWK]:
        try:
            with self._opener.open(self._jwks_url, timeout=self._request_timeout) as response:
                data = response.read(self._max_jwks_bytes + 1)
        except HTTPError as error:
            error.close()
            raise
        if len(data) > self._max_jwks_bytes:
            raise ValueError("JWKS response exceeds the size limit.")
        document = json.loads(data)
        if not isinstance(document, dict) or not isinstance(document.get("keys"), list):
            raise ValueError("Invalid JWKS document.")

        keys = {}
        for item in document["keys"]:
            if not isinstance(item, dict):
                raise ValueError("Invalid JWKS key.")
            if item.get("kty") != "RSA" or item.get("alg", "RS256") != "RS256":
                continue
            if item.get("use", "sig") != "sig":
                continue
            kid = item.get("kid")
            if not isinstance(kid, str) or not kid or kid in keys:
                raise ValueError("Invalid JWKS signing key ID.")
            key = jwt.PyJWK.from_dict(item, algorithm="RS256")
            if key.key.key_size < 2048:
                raise ValueError("JWKS signing key is too small.")
            keys[kid] = key
        if not keys:
            raise ValueError("JWKS has no eligible signing keys.")
        return keys
