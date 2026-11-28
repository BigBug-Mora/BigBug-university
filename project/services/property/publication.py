"""Seller-owned showcase authoring and atomic publication."""

from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.types.json import Jsonb

from . import drafts
from .database import owned_listing
from .publication_facts import reconcile


def encode(value):
    return jsonable_encoder(value, custom_encoder={Decimal: str})


def showcase(db, listing, showcase_id):
    return db.execute(
        "SELECT * FROM property.showcase_revisions WHERE listing_id=%s AND id=%s",
        (listing, showcase_id),
    ).fetchone()


def save_showcase(db, listing, seller, command):
    current = owned_listing(db, listing, seller, lock=True)
    replay = db.execute(
        "SELECT * FROM property.showcase_revisions WHERE listing_id=%s AND action_id=%s",
        (listing, command.action_id),
    ).fetchone()
    if replay:
        return encode(replay)
    if command.source_revision_id != current["current_draft_revision_id"]:
        raise HTTPException(409, "The draft changed. Save a showcase for the current revision.")
    if command.parent_showcase_id != current["current_showcase_id"]:
        raise HTTPException(409, "The showcase changed. Reopen it before saving.")
    row = db.execute(
        """INSERT INTO property.showcase_revisions
        (id,listing_id,source_revision_id,parent_showcase_id,action_id,headline,description,highlights)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
        (uuid4(), listing, command.source_revision_id, command.parent_showcase_id,
         command.action_id, command.headline, command.description, Jsonb(command.highlights)),
    ).fetchone()
    db.execute("UPDATE property.listings SET current_showcase_id=%s WHERE id=%s", (row["id"], listing))
    return encode(row)


def summary(db, listing, *, action=None):
    return db.execute(
        """SELECT p.id AS publication_id,p.listing_id,p.listing_revision_id,p.showcase_id,
                  p.published_at,r.revision_no
           FROM property.publications p
           JOIN property.listing_revisions r ON r.id=p.listing_revision_id """
        + ("WHERE p.listing_id=%s AND p.action_id=%s" if action else
           "JOIN property.current_publications cp ON cp.publication_id=p.id WHERE cp.listing_id=%s"),
        (listing, action) if action else (listing,),
    ).fetchone()


def missing_requirements(db, listing, revision):
    required = ["district", "town", "price_basis", "entered_price", "currency"]
    if revision["property_type"] in ("house", "land"):
        required += ["land_area", "land_area_unit"]
    if revision["property_type"] == "house":
        required += ["bedroom_count", "bathroom_count"]
    if revision["property_type"] == "apartment":
        required += ["floor_area", "floor_area_unit"]
    missing = [key for key in required if revision[key] is None]
    count = db.execute(
        """SELECT count(*) AS n FROM property.private_details
           WHERE listing_id=%s AND detail_kind='phone' AND retired_at IS NULL""", (listing,),
    ).fetchone()["n"]
    if not 1 <= count <= 3:
        missing.append("1–3 active private phone numbers")
    return missing


def preview(db, listing, seller):
    current = owned_listing(db, listing, seller, lock=True)
    draft = drafts.revision(db, listing, current["current_draft_revision_id"])
    authored = showcase(db, listing, current["current_showcase_id"])
    matches = bool(authored and authored["source_revision_id"] == current["current_draft_revision_id"])
    missing = missing_requirements(db, listing, draft["revision"])
    if not matches:
        missing.append("A showcase matching the current draft")
    return encode({**draft, "showcase": authored, "showcase_matches_draft": matches,
                   "publication": summary(db, listing), "missing_requirements": missing,
                   "gallery_photos": [], "featured_photos": []})


def publish(db, listing, seller, command):
    current = owned_listing(db, listing, seller, lock=True)
    replay = summary(db, listing, action=command.action_id)
    if replay:
        return encode(replay)
    authored = showcase(db, listing, command.showcase_id)
    if (command.listing_revision_id != current["current_draft_revision_id"]
            or command.showcase_id != current["current_showcase_id"]
            or not authored or authored["source_revision_id"] != command.listing_revision_id):
        raise HTTPException(409, "Publish the current draft with a matching showcase. Reopen the preview.")
    revision = db.execute("SELECT * FROM property.listing_revisions WHERE id=%s",
                          (command.listing_revision_id,)).fetchone()
    missing = missing_requirements(db, listing, revision)
    if missing:
        raise HTTPException(422, "Publication requires: " + ", ".join(missing) + ".")
    outgoing = summary(db, listing)
    reconcile(db, listing, outgoing["listing_revision_id"] if outgoing else None, revision)
    publication_id = uuid4()
    db.execute(
        """INSERT INTO property.publications
        (id,listing_id,listing_revision_id,showcase_id,published_by,action_id)
        VALUES (%s,%s,%s,%s,%s,%s)""",
        (publication_id, listing, command.listing_revision_id, command.showcase_id, seller, command.action_id),
    )
    db.execute(
        """INSERT INTO property.current_publications (listing_id,publication_id) VALUES (%s,%s)
           ON CONFLICT (listing_id) DO UPDATE SET publication_id=EXCLUDED.publication_id""",
        (listing, publication_id),
    )
    return encode(summary(db, listing))
