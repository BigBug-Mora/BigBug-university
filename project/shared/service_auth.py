"""Authenticate callers using receiver-scoped credentials."""

from collections.abc import Mapping
from hmac import compare_digest


SERVICE_TOKEN_HEADER = "X-EstateFlow-Service-Token"


class ServiceAuthenticator:
    def __init__(self, credentials: Mapping[str, str]) -> None:
        if not credentials or any(not secret or not secret.isascii() for secret in credentials.values()):
            raise ValueError("Configure nonempty ASCII service credentials.")
        if len(set(credentials.values())) != len(credentials):
            raise ValueError("Configure a distinct service credential for each caller.")
        self._credentials = {caller: secret.encode("ascii") for caller, secret in credentials.items()}

    def authenticate(self, credential: str | None) -> str | None:
        if not credential or not credential.isascii():
            return None
        supplied = credential.encode("ascii")
        matched = None
        for caller, expected in self._credentials.items():
            if compare_digest(supplied, expected):
                matched = caller
        return matched
