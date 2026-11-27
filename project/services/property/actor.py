"""Derive the authenticated actor for protected Property operations."""

from collections.abc import Collection
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request

from project.services.property.engagement import AccountForbidden, EngagementResolver, ResolverUnavailable
from project.shared.cognito import CognitoVerifier, InvalidAccessToken, VerificationUnavailable
from project.shared.service_auth import SERVICE_TOKEN_HEADER, ServiceAuthenticator


NO_STORE = {"Cache-Control": "no-store"}


@dataclass(frozen=True)
class Actor:
    account_id: UUID


class ActorAuthentication:
    def __init__(
        self,
        verifier: CognitoVerifier,
        caller_auth: ServiceAuthenticator,
        engagement: EngagementResolver,
    ) -> None:
        self._verifier = verifier
        self._caller_auth = caller_auth
        self._engagement = engagement

    def require(self, request: Request, allowed_callers: Collection[str]) -> Actor:
        credentials = request.headers.getlist(SERVICE_TOKEN_HEADER)
        caller = self._caller_auth.authenticate(credentials[0]) if len(credentials) == 1 else None
        if caller is None:
            raise HTTPException(401, "Unauthorized", headers=NO_STORE)
        if caller not in allowed_callers:
            raise HTTPException(403, "Forbidden", headers=NO_STORE)

        authorizations = request.headers.getlist("Authorization")
        if len(authorizations) != 1:
            raise HTTPException(401, "Unauthorized", headers=NO_STORE)
        authorization = authorizations[0]
        try:
            self._verifier.verify_bearer(authorization)
            return Actor(self._engagement.resolve(authorization))
        except InvalidAccessToken:
            raise HTTPException(401, "Unauthorized", headers=NO_STORE) from None
        except AccountForbidden:
            raise HTTPException(403, "Forbidden", headers=NO_STORE) from None
        except (VerificationUnavailable, ResolverUnavailable):
            raise HTTPException(503, "Service unavailable", headers=NO_STORE) from None
