BEGIN;
GRANT USAGE ON SCHEMA property TO estateflow_property;
GRANT SELECT, INSERT ON property.listings, property.listing_revisions,
    property.fact_versions, property.revision_facts TO estateflow_property;
GRANT UPDATE (current_draft_revision_id) ON property.listings TO estateflow_property;
GRANT SELECT, INSERT, UPDATE (encrypted_value, encryption_key_ref, updated_at, retired_at)
    ON property.private_details TO estateflow_property;
COMMIT;
