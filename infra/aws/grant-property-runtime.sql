BEGIN;
GRANT USAGE ON SCHEMA property TO estateflow_property;
GRANT SELECT (id, seller_account_id, create_action_id, current_draft_revision_id),
      INSERT (id, seller_account_id, create_action_id) ON property.listings TO estateflow_property;
GRANT SELECT (fact_key, property_type) ON property.fact_applicability TO estateflow_property;
GRANT SELECT, INSERT ON property.listing_revisions,
    property.fact_versions, property.revision_facts TO estateflow_property;
GRANT UPDATE (current_draft_revision_id) ON property.listings TO estateflow_property;
GRANT SELECT, INSERT, UPDATE (encrypted_value, encryption_key_ref, updated_at, retired_at)
    ON property.private_details TO estateflow_property;
COMMIT;
