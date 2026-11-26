DO $$
DECLARE
    property_types text[];
    published_plot property.public_listings%ROWTYPE;
BEGIN
    IF current_user <> 'estateflow_migrator' OR EXISTS (
        SELECT FROM pg_roles
        WHERE rolname = current_user AND (rolsuper OR rolcreaterole OR rolcreatedb)
    ) THEN
        RAISE EXCEPTION 'Database checks must run under the migration owner without server administration privileges';
    END IF;

    IF (SELECT count(*) FROM pg_namespace
        WHERE nspname IN ('account', 'property', 'engagement', 'agent')
          AND pg_get_userbyid(nspowner) = current_user) <> 4 THEN
        RAISE EXCEPTION 'The migration owner must own all four application schemas';
    END IF;

    IF (SELECT count(*) FROM property.area_units) <> 5
       OR (SELECT count(*) FROM property.fact_definitions) <> 3
       OR (SELECT count(*) FROM property.fact_applicability) <> 8 THEN
        RAISE EXCEPTION 'Required reference data is incomplete';
    END IF;

    SELECT array_agg(revision.property_type::text ORDER BY revision.property_type)
    INTO property_types
    FROM property.listings AS listing
    JOIN property.listing_revisions AS revision
      ON revision.listing_id = listing.id AND revision.id = listing.current_draft_revision_id;

    IF property_types IS DISTINCT FROM ARRAY['apartment', 'house', 'land'] THEN
        RAISE EXCEPTION 'Expected one current draft of each type, found %', property_types;
    END IF;

    IF NOT EXISTS (
        SELECT FROM property.listing_revisions
        WHERE property_type = 'house' AND vehicle_access IS NULL AND parking_spaces IS NULL
    ) OR NOT EXISTS (
        SELECT FROM property.listing_revisions
        WHERE property_type = 'apartment' AND vehicle_access IS FALSE AND parking_spaces = 0
    ) THEN
        RAISE EXCEPTION 'Draft facts must preserve unknown, false and zero';
    END IF;

    SELECT * INTO STRICT published_plot FROM property.public_listings;
    IF published_plot.property_type IS DISTINCT FROM 'land'
       OR published_plot.price_basis IS DISTINCT FROM 'per_unit'
       OR published_plot.price_area_unit IS DISTINCT FROM 'perch'
       OR published_plot.entered_price IS DISTINCT FROM 250000
       OR published_plot.total_asking_price IS DISTINCT FROM 5000000
       OR published_plot.total_derived_from_approximate_area IS DISTINCT FROM true
       OR published_plot.vehicle_access IS DISTINCT FROM true THEN
        RAISE EXCEPTION 'Public view must expose only the published land with its converted price and access';
    END IF;
END
$$;
