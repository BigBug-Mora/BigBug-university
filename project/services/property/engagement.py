"""Resolve verified Property callers' accounts through Engagement."""

import json
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from urllib.parse import urlsplit
from uuid import UUID

from project.shared.service_auth import SERVICE_TOKEN_HEADER


class AccountForbidden(Exception):
    pass


class ResolverUnavailable(Exception):
    pass


class EngagementResolver:
    _timeout = 2
    _max_response_bytes = 4096

    def __init__(self, origin: str, service_token: str) -> None:
        url = urlsplit(origin)
        if (
            url.scheme not in ("http", "https")
            or not url.hostname
            or url.username is not None
            or url.path not in ("", "/")
            or url.query
            or url.fragment
        ):
            raise ValueError("Configure an HTTP or HTTPS origin for Engagement.")
        self._connection = HTTPSConnection if url.scheme == "https" else HTTPConnection
        self._host = url.hostname
        self._port = url.port
        self._service_token = service_token

    def resolve(self, authorization: str) -> UUID:
        connection = self._connection(self._host, self._port, timeout=self._timeout)
        try:
            connection.request("POST", "/internal/accounts/resolve", headers={
                "Authorization": authorization,
                SERVICE_TOKEN_HEADER: self._service_token,
            })
            with connection.getresponse() as response:
                if response.status == 403:
                    raise AccountForbidden
                if response.status != 200:
                    raise ResolverUnavailable
                data = response.read(self._max_response_bytes + 1)
            if len(data) > self._max_response_bytes:
                raise ResolverUnavailable
            result = json.loads(data)
            if not isinstance(result, dict) or not isinstance(result.get("account_id"), str):
                raise ResolverUnavailable
            account_id = UUID(result["account_id"])
            if str(account_id) != result["account_id"].lower():
                raise ResolverUnavailable
            return account_id
        except (OSError, HTTPException, ValueError, RecursionError):
            raise ResolverUnavailable from None
        finally:
            connection.close()
