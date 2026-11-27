from uuid import UUID

from fastapi import APIRouter, Depends

from . import drafts
from .database import owned_listing, transaction
from .models import CreateDraft, SaveDraft
from .private_details import private_routes


def listing_routes(require_frontend_actor):
    router = APIRouter(prefix="/listings")
    actor = Depends(require_frontend_actor)

    @router.post("")
    def create(command: CreateDraft, seller=actor):
        with transaction() as db:
            return drafts.create(db, seller.account_id, command)

    @router.get("")
    def index(seller=actor):
        with transaction() as db:
            return drafts.list_owned(db, seller.account_id)

    @router.get("/{listing_id}")
    def get(listing_id: UUID, seller=actor):
        with transaction() as db:
            listing = owned_listing(db, listing_id, seller.account_id)
            return drafts.revision(db, listing_id, listing["current_draft_revision_id"])

    @router.post("/{listing_id}/revisions")
    def save(listing_id: UUID, command: SaveDraft, seller=actor):
        with transaction() as db:
            return drafts.save(db, listing_id, seller.account_id, command)

    router.include_router(private_routes(require_frontend_actor))
    return router
