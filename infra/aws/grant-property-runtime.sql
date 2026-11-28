BEGIN;
GRANT USAGE ON SCHEMA property TO estateflow_property;
GRANT SELECT (id, seller_account_id, create_action_id, current_draft_revision_id, current_showcase_id),
      INSERT (id, seller_account_id, create_action_id) ON property.listings TO estateflow_property;
GRANT SELECT (fact_key, property_type) ON property.fact_applicability TO estateflow_property;
GRANT SELECT (fact_key, display_name, value_kind, canonical_unit, storage_kind)
    ON property.fact_definitions TO estateflow_property;
GRANT SELECT (code, square_metres, valid_for_floor_area) ON property.area_units TO estateflow_property;
GRANT SELECT, INSERT ON property.listing_revisions,
    property.fact_versions, property.revision_facts,
    property.showcase_revisions, property.publications TO estateflow_property;
GRANT SELECT, INSERT, UPDATE (publication_id) ON property.current_publications TO estateflow_property;
GRANT SELECT, INSERT, UPDATE (fact_version_id, field_revision_id), DELETE
    ON property.buyer_visible_facts TO estateflow_property;
GRANT SELECT ON property.public_listings, property.showcase_photos,
    property.showcase_featured_photos TO estateflow_property;
GRANT UPDATE (current_draft_revision_id, current_showcase_id) ON property.listings TO estateflow_property;
GRANT SELECT, INSERT, UPDATE (encrypted_value, encryption_key_ref, updated_at, retired_at)
    ON property.private_details TO estateflow_property;
COMMIT;
