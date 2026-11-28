from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg import sql
from psycopg.types.json import Jsonb

from .database import owned_listing
from .models import Draft


def revision(db, listing, revision_id):
    row = db.execute(
        "SELECT * FROM property.listing_revisions WHERE listing_id=%s AND id=%s", (listing, revision_id)
    ).fetchone()
    facts = db.execute(
        """
        SELECT f.*, r.approved_for_public FROM property.revision_facts r
        JOIN property.fact_versions f ON f.id=r.fact_version_id
        WHERE r.revision_id=%s ORDER BY r.fact_key
    """,
        (revision_id,),
    ).fetchall()
    return jsonable_encoder(
        {"listing_id": listing, "revision": row, "facts": facts}, custom_encoder={Decimal: str}
    )


def list_owned(db, seller):
    return jsonable_encoder(
        db.execute(
            """
            SELECT l.id, r.property_type, r.town, r.district, r.revision_no,
                   p.published_at, pr.revision_no AS published_revision_no
            FROM property.listings l
            JOIN property.listing_revisions r ON r.id=l.current_draft_revision_id
            LEFT JOIN property.current_publications cp ON cp.listing_id=l.id
            LEFT JOIN property.publications p ON p.id=cp.publication_id
            LEFT JOIN property.listing_revisions pr ON pr.id=p.listing_revision_id
            WHERE l.seller_account_id=%s ORDER BY r.created_at DESC, l.id
        """,
            (seller,),
        ).fetchall()
    )


def create(db, seller, command):
    listing = uuid4()
    inserted = db.execute(
        """
        INSERT INTO property.listings (id, seller_account_id, create_action_id)
        VALUES (%s,%s,%s) ON CONFLICT (seller_account_id,create_action_id) DO NOTHING RETURNING id
    """,
        (listing, seller, command.create_action_id),
    ).fetchone()
    if not inserted:
        original = db.execute(
            """
            SELECT r.listing_id,r.id FROM property.listings l JOIN property.listing_revisions r
            ON r.listing_id=l.id AND r.revision_no=1 WHERE seller_account_id=%s AND create_action_id=%s
        """,
            (seller, command.create_action_id),
        ).fetchone()
        return revision(db, original["listing_id"], original["id"])
    return write(db, listing, seller, uuid4(), None, 1, command.draft)


def save(db, listing, seller, command):
    current = owned_listing(db, listing, seller, lock=True)["current_draft_revision_id"]
    existing = db.execute(
        """SELECT id FROM property.listing_revisions
                             WHERE listing_id=%s AND edit_action_id=%s""",
        (listing, command.edit_action_id),
    ).fetchone()
    if existing:
        return revision(db, listing, existing["id"])
    if current != command.parent_revision_id:
        raise HTTPException(409, "Another revision has been saved. Reopen the draft to review it.")
    parent = db.execute(
        "SELECT revision_no FROM property.listing_revisions WHERE id=%s", (current,)
    ).fetchone()
    return write(
        db, listing, seller, command.edit_action_id, current, parent["revision_no"] + 1, command.draft
    )


def write(db, listing, seller, action, parent, number, draft: Draft):
    revision_id = uuid4()
    values = draft.model_dump(
        exclude={"access_road_width", "access_road_width_approved_for_public"}
    )
    evidence = values.pop("standard_fact_evidence")
    for field, value in values.items():
        if value is not None:
            evidence.setdefault(field, {"source_kind": "seller"})
    values["standard_fact_evidence"] = Jsonb(evidence)
    values.update(
        id=revision_id,
        listing_id=listing,
        created_by_account_id=seller,
        edit_action_id=action,
        parent_revision_id=parent,
        revision_no=number,
    )
    db.execute(
        sql.SQL("INSERT INTO property.listing_revisions ({}) VALUES ({})").format(
            sql.SQL(",").join(map(sql.Identifier, values)),
            sql.SQL(",").join(sql.Placeholder() for _ in values),
        ),
        tuple(values.values()),
    )
    width = draft.access_road_width
    # Omission preserves the parent's link. Explicit null clears the width.
    replace_width = "access_road_width" in draft.model_fields_set
    approval_set = (
        "access_road_width_approved_for_public" in draft.model_fields_set
        and draft.access_road_width_approved_for_public is not None
    )
    if parent and replace_width and width:
        same = db.execute(
            """
            SELECT 1 FROM property.revision_facts r JOIN property.fact_versions f ON f.id=r.fact_version_id
            WHERE r.revision_id=%s AND r.fact_key='access_road_width' AND f.number_value=%s
            AND f.unit=%s AND f.approximate IS NOT DISTINCT FROM %s AND f.source_kind=%s
            AND f.qualifier IS NOT DISTINCT FROM %s
        """,
            (
                parent,
                width.number_value,
                width.unit,
                width.approximate,
                width.source_kind,
                width.qualifier,
            ),
        ).fetchone()
        replace_width = not same
    if parent:
        if not replace_width and approval_set:
            flag = bool(draft.access_road_width_approved_for_public)
            db.execute(
                """
                INSERT INTO property.revision_facts
                SELECT listing_id,%s,fact_key,fact_version_id,
                       CASE WHEN fact_key='access_road_width' THEN %s ELSE approved_for_public END,
                       CASE WHEN fact_key='access_road_width' THEN (CASE WHEN %s THEN %s ELSE NULL END) ELSE approved_by END,
                       CASE WHEN fact_key='access_road_width' THEN (CASE WHEN %s THEN now() ELSE NULL END) ELSE approved_at END
                FROM property.revision_facts WHERE revision_id=%s
            """,
                (revision_id, flag, flag, seller, flag, parent),
            )
        else:
            db.execute(
                """
                INSERT INTO property.revision_facts
                SELECT listing_id,%s,fact_key,fact_version_id,approved_for_public,approved_by,approved_at
                FROM property.revision_facts WHERE revision_id=%s AND (NOT %s OR fact_key <> 'access_road_width')
            """,
                (revision_id, parent, replace_width),
            )
    if replace_width and width:
        applicable = db.execute(
            """SELECT 1 FROM property.fact_applicability
                                   WHERE fact_key='access_road_width' AND property_type=%s""",
            (draft.property_type,),
        ).fetchone()
        if not applicable:
            raise HTTPException(422, "Road width is unavailable for this property type.")
        version = uuid4()
        db.execute(
            """
            INSERT INTO property.fact_versions (id,listing_id,fact_key,version_no,value_kind,evidence_state,
                number_value,unit,approximate,qualifier,source_kind,source_account_id)
            SELECT %s,%s,'access_road_width',coalesce(max(version_no),0)+1,'number','known',
                   %s,%s,%s,%s,%s,%s FROM property.fact_versions WHERE listing_id=%s AND fact_key='access_road_width'
        """,
            (
                version,
                listing,
                width.number_value,
                width.unit,
                width.approximate,
                width.qualifier,
                width.source_kind,
                seller,
                listing,
            ),
        )
        flag = bool(draft.access_road_width_approved_for_public) if approval_set else False
        db.execute(
            """INSERT INTO property.revision_facts
                      (listing_id,revision_id,fact_key,fact_version_id,approved_for_public,approved_by,approved_at)
                      VALUES (%s,%s,'access_road_width',%s,%s,CASE WHEN %s THEN %s ELSE NULL END,CASE WHEN %s THEN now() ELSE NULL END)""",
            (listing, revision_id, version, flag, flag, seller, flag),
        )
    db.execute(
        "UPDATE property.listings SET current_draft_revision_id=%s WHERE id=%s", (revision_id, listing)
    )
    return revision(db, listing, revision_id)
