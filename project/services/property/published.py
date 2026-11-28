"""Allowlisted buyer projection, anchored exclusively to a live publication."""

from fastapi import HTTPException
from psycopg import sql

# Dedicated revision columns not already supplied by property.public_listings.
DETAIL_FIELDS = (
    "revision_no", "price_negotiable", "attached_bathroom_count", "separate_toilet_count",
    "house_storey_count", "apartment_floor_no", "ground_floor_bedrooms", "parking_spaces",
    "covered_parking_spaces", "construction_status", "year_built", "furnishing_status",
    "has_mains_water", "has_well_water", "has_electricity", "has_garden", "has_boundary_wall",
    "standard_fact_evidence",
)


def read(db, listing):
    row = db.execute(
        sql.SQL("""SELECT v.*,{} FROM property.current_publications cp
                   JOIN property.public_listings v ON v.listing_id=cp.listing_id
                   JOIN property.listing_revisions r ON r.id=v.listing_revision_id
                   WHERE cp.listing_id=%s""").format(
            sql.SQL(",").join(sql.Identifier("r", field) for field in DETAIL_FIELDS)),
        (listing,),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Listing unavailable")
    row["facts"] = db.execute(
        """SELECT d.display_name,f.fact_key,f.value_kind,f.evidence_state,
                  f.number_value,f.boolean_value,f.text_value,f.unit,f.approximate,
                  f.source_kind,f.qualifier,f.certainty
           FROM property.revision_facts rf
           JOIN property.fact_versions f ON f.id=rf.fact_version_id
           JOIN property.fact_definitions d ON d.fact_key=f.fact_key
           WHERE rf.listing_id=%s AND rf.revision_id=%s AND rf.approved_for_public
           ORDER BY f.fact_key""", (listing, row["listing_revision_id"]),
    ).fetchall()
    row["gallery_photos"] = db.execute(
        """SELECT photo_id,display_order,caption FROM property.showcase_photos
           WHERE showcase_id=%s ORDER BY display_order""", (row["showcase_id"],),
    ).fetchall()
    row["featured_photos"] = db.execute(
        """SELECT photo_id,feature_order,title,body FROM property.showcase_featured_photos
           WHERE showcase_id=%s ORDER BY feature_order""", (row["showcase_id"],),
    ).fetchall()
    return row
