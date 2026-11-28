"""Reconcile chat pointers against the outgoing and incoming public selections."""

# These are the only registered dedicated inquiry mappings in the MVP.
DEDICATED_FIELDS = ("bedroom_count", "covered_parking_spaces")


def approved(db, revision):
    return {row["fact_key"]: row["fact_version_id"] for row in db.execute(
        """SELECT fact_key,fact_version_id FROM property.revision_facts
           WHERE revision_id=%s AND approved_for_public""", (revision,),
    ).fetchall()}


def field_value(revision, key):
    evidence = revision["standard_fact_evidence"].get(key) or {}
    # Form round trips expand omitted optional metadata to null. Neither changes
    # the evidence reviewed by the seller or supersedes an independent answer.
    return revision[key], {name: value for name, value in evidence.items() if value is not None}


def reconcile(db, listing, outgoing_id, incoming):
    old = approved(db, outgoing_id)
    new = approved(db, incoming["id"])
    for key, version in new.items():
        if old.get(key) != version:
            db.execute(
                """INSERT INTO property.buyer_visible_facts (listing_id,fact_key,fact_version_id)
                   VALUES (%s,%s,%s) ON CONFLICT (listing_id,fact_key)
                   DO UPDATE SET fact_version_id=EXCLUDED.fact_version_id,field_revision_id=NULL""",
                (listing, key, version),
            )
    for key in old.keys() - new.keys():
        db.execute(
            """DELETE FROM property.buyer_visible_facts
               WHERE listing_id=%s AND fact_key=%s AND fact_version_id=%s""",
            (listing, key, old[key]),
        )
    outgoing = db.execute("SELECT * FROM property.listing_revisions WHERE id=%s",
                          (outgoing_id,)).fetchone() if outgoing_id else None
    for key in DEDICATED_FIELDS:
        before = field_value(outgoing, key) if outgoing else (None, None)
        after = field_value(incoming, key)
        if before == after:
            continue
        if after[0] is not None:
            db.execute("DELETE FROM property.buyer_visible_facts WHERE listing_id=%s AND fact_key=%s",
                       (listing, key))
        elif outgoing:
            pointer = db.execute(
                """SELECT r.* FROM property.buyer_visible_facts b
                   JOIN property.listing_revisions r ON r.id=b.field_revision_id
                   WHERE b.listing_id=%s AND b.fact_key=%s""", (listing, key),
            ).fetchone()
            if pointer and field_value(pointer, key) == before:
                db.execute("DELETE FROM property.buyer_visible_facts WHERE listing_id=%s AND fact_key=%s",
                           (listing, key))
