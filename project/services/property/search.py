"""Structured filters over the published projection; no seller/private reads."""

from decimal import Decimal

from fastapi.encoders import jsonable_encoder
from psycopg import sql

from .models import SearchQuery


def literal_substring(value):
    return "%" + value.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"


def filters(query: SearchQuery):
    clauses, values = [], []
    for key in ("property_type", "currency"):
        value = getattr(query, key)
        if value is not None:
            clauses.append(sql.SQL("v.{} = %s").format(sql.Identifier(key)))
            values.append(value)
    for key in ("district", "town"):
        value = getattr(query, key)
        if value is not None:
            clauses.append(sql.SQL("v.{} ILIKE %s ESCAPE '!'").format(sql.Identifier(key)))
            values.append(literal_substring(value))
    for value, column, operator in (
        (query.min_price, "total_asking_price", ">="), (query.max_price, "total_asking_price", "<="),
        (query.min_bedrooms, "bedroom_count", ">="), (query.min_bathrooms, "bathroom_count", ">="),
    ):
        if value is not None:
            clauses.append(sql.SQL("v.{} {} %s").format(sql.Identifier(column), sql.SQL(operator)))
            values.append(value)
    for area, unit, column, alias in (
        (query.min_land_area, query.land_area_unit, "land_area", "land_unit"),
        (query.min_floor_area, query.floor_area_unit, "floor_area", "floor_unit"),
    ):
        if area is not None:
            clauses.append(sql.SQL("""v.{} * {}.square_metres >= %s *
                (SELECT square_metres FROM property.area_units WHERE code=%s)""").format(
                    sql.Identifier(column), sql.Identifier(alias)))
            values.extend((area, unit))
    vehicle_clause = {"required": "v.vehicle_access IS NOT FALSE", "confirmed": "v.vehicle_access IS TRUE",
                      "none": "v.vehicle_access IS FALSE"}.get(query.vehicle_access)
    if vehicle_clause:
        clauses.append(sql.SQL(vehicle_clause))
    return sql.SQL(" AND ").join(clauses) if clauses else sql.SQL("TRUE"), values


def search(db, query: SearchQuery):
    where, values = filters(query)
    # MATERIALIZED and the lateral page preserve an exact total even beyond the
    # final page, in the same statement snapshot as the returned records.
    statement = sql.SQL("""
        WITH matches AS MATERIALIZED (
            SELECT v.*,
                   CASE WHEN v.vehicle_access THEN 'confirmed'
                        WHEN v.vehicle_access IS FALSE THEN 'false' ELSE 'unknown' END AS vehicle_access_status,
                   CASE WHEN %s AND v.vehicle_access IS NULL THEN 'needs_confirmation'
                        ELSE 'matched' END AS match_status,
                   NULL AS cover_photo
            FROM property.public_listings v
            LEFT JOIN property.area_units land_unit ON land_unit.code=v.land_area_unit
            LEFT JOIN property.area_units floor_unit ON floor_unit.code=v.floor_area_unit
            WHERE {}
        )
        SELECT totals.search_total, page.* FROM (SELECT count(*) AS search_total FROM matches) totals
        LEFT JOIN LATERAL (
            SELECT * FROM matches
            ORDER BY (match_status='needs_confirmation') ASC, published_at DESC, listing_id ASC
            LIMIT %s OFFSET %s
        ) page ON TRUE
    """).format(where)
    rows = db.execute(statement, [query.vehicle_access == "required", *values, query.limit, query.offset]).fetchall()
    total = rows[0]["search_total"]
    items = [{key: value for key, value in row.items() if key != "search_total"}
             for row in rows if row["listing_id"] is not None]
    return jsonable_encoder({"items": items, "total": total, "limit": query.limit, "offset": query.offset},
                            custom_encoder={Decimal: str})
