import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from project.services.property.actor import NO_STORE, Actor, ActorAuthentication
from project.services.property.engagement import EngagementResolver
from project.services.property.routes import listing_routes, published_routes
from project.shared.cognito import CognitoVerifier
from project.shared.service_auth import ServiceAuthenticator


class AccountIdentity(BaseModel):
    account_id: UUID


def build_app(authentication: ActorAuthentication | None = None) -> FastAPI:
    app = FastAPI(title="EstateFlow Property Service")

    @app.middleware("http")
    async def draft_cache_policy(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.split("/", 2)[1:2] in (["listings"], ["published-listings"]):
            response.headers.update(NO_STORE)
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        # Framework validation can include submitted values, including private details.
        return JSONResponse({"detail": "Check the requested fields and their types."},
                            status_code=422, headers=NO_STORE)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    def require_frontend_actor(request: Request) -> Actor:
        if authentication is None:
            raise HTTPException(503, "Service unavailable", headers=NO_STORE)
        return authentication.require(request, {"frontend"})

    @app.get("/internal/identity/me")
    def identity(
        actor: Annotated[Actor, Depends(require_frontend_actor)],
        response: Response,
    ) -> AccountIdentity:
        response.headers.update(NO_STORE)
        return AccountIdentity(account_id=actor.account_id)

    app.include_router(listing_routes(require_frontend_actor))
    app.include_router(published_routes(require_frontend_actor))
    return app


def create_app() -> FastAPI:
    engagement_origin = os.getenv("ESTATEFLOW_ENGAGEMENT_BASE_URL")
    frontend_token = os.getenv("ESTATEFLOW_FRONTEND_TO_PROPERTY_TOKEN")
    engagement_token = os.getenv("ESTATEFLOW_PROPERTY_TO_ENGAGEMENT_TOKEN")
    if not any((engagement_origin, frontend_token, engagement_token)):
        return build_app()
    if not all((engagement_origin, frontend_token, engagement_token)):
        raise ValueError("Configure Property's Engagement origin and both service credentials.")
    if frontend_token == engagement_token or not engagement_token.isascii():
        raise ValueError("Configure distinct ASCII service credentials for Property.")

    return build_app(ActorAuthentication(
        CognitoVerifier(
            os.environ["ESTATEFLOW_COGNITO_ISSUER"],
            os.environ["ESTATEFLOW_COGNITO_CLIENT_ID"],
            allow_insecure_http=os.getenv("ESTATEFLOW_TEST_ALLOW_HTTP_ISSUER") == "1",
        ),
        ServiceAuthenticator({"frontend": frontend_token}),
        EngagementResolver(engagement_origin, engagement_token),
    ))
