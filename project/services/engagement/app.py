"""Engagement's internal HTTP API."""

import os
from collections.abc import Collection
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from project.services.engagement.accounts import AccountStore, AccountStoreUnavailable, DisabledAccount
from project.shared.cognito import CognitoVerifier, InvalidAccessToken, VerificationUnavailable
from project.shared.service_auth import SERVICE_TOKEN_HEADER, ServiceAuthenticator


NO_STORE = {"Cache-Control": "no-store"}


class ResolvedAccount(BaseModel):
    account_id: UUID


def build_app(
    store: AccountStore,
    verifier: CognitoVerifier,
    caller_auth: ServiceAuthenticator,
    resolver_callers: Collection[str],
) -> FastAPI:
    app = FastAPI(title="EstateFlow Engagement")

    @app.post("/internal/accounts/resolve")
    def resolve_account(request: Request, response: Response) -> ResolvedAccount:
        credentials = request.headers.getlist(SERVICE_TOKEN_HEADER)
        caller = caller_auth.authenticate(credentials[0]) if len(credentials) == 1 else None
        if caller is None:
            raise HTTPException(401, "Unauthorized", headers=NO_STORE)
        if caller not in resolver_callers:
            raise HTTPException(403, "Forbidden", headers=NO_STORE)

        authorization = request.headers.getlist("Authorization")
        try:
            identity = verifier.verify_bearer(authorization[0] if len(authorization) == 1 else None)
            account_id = store.resolve(identity)
        except InvalidAccessToken:
            raise HTTPException(401, "Unauthorized", headers=NO_STORE) from None
        except DisabledAccount:
            raise HTTPException(403, "Forbidden", headers=NO_STORE) from None
        except (VerificationUnavailable, AccountStoreUnavailable):
            raise HTTPException(503, "Service unavailable", headers=NO_STORE) from None

        response.headers.update(NO_STORE)
        return ResolvedAccount(account_id=account_id)

    return app


def create_app() -> FastAPI:
    callers = {
        "frontend": os.environ["ESTATEFLOW_FRONTEND_TO_ENGAGEMENT_TOKEN"],
        "property": os.environ["ESTATEFLOW_PROPERTY_TO_ENGAGEMENT_TOKEN"],
    }
    return build_app(
        AccountStore(os.environ["ESTATEFLOW_ENGAGEMENT_DATABASE_URL"]),
        CognitoVerifier(
            os.environ["ESTATEFLOW_COGNITO_ISSUER"],
            os.environ["ESTATEFLOW_COGNITO_CLIENT_ID"],
            allow_insecure_http=os.getenv("ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER") == "1",
        ),
        ServiceAuthenticator(callers),
        frozenset(callers),
    )
