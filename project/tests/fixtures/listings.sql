-- Only loaded by the disposable Compose database fixture command.
DO $$
DECLARE
    seller_id constant uuid := '10000000-0000-4000-8000-000000000001';
    house_id uuid := gen_random_uuid();
    apartment_id uuid := gen_random_uuid();
    land_id uuid := gen_random_uuid();
    house_revision_id uuid := gen_random_uuid();
    apartment_revision_id uuid := gen_random_uuid();
    land_revision_id uuid := gen_random_uuid();
    showcase_id uuid := gen_random_uuid();
    publication_id uuid := gen_random_uuid();
BEGIN
    -- Claim the fixture set in the same transaction as its dependent rows.
    INSERT INTO account.accounts (id, cognito_issuer, cognito_subject)
    VALUES (seller_id, 'https://identity.example.invalid', 'estateflow-fixture-seller')
    ON CONFLICT (id) DO NOTHING;
    IF NOT FOUND THEN
        RETURN;
    END IF;

    INSERT INTO account.profiles (account_id, display_name)
    VALUES (seller_id, 'Fictional EstateFlow Seller');

    INSERT INTO property.listings (id, seller_account_id, create_action_id)
    VALUES (house_id, seller_id, gen_random_uuid()),
           (apartment_id, seller_id, gen_random_uuid()),
           (land_id, seller_id, gen_random_uuid());

    INSERT INTO property.listing_revisions (
        id, listing_id, revision_no, edit_action_id, created_by_account_id,
        property_type, vehicle_access, parking_spaces
    )
    VALUES (house_revision_id, house_id, 1, gen_random_uuid(), seller_id, 'house', NULL, NULL),
           (apartment_revision_id, apartment_id, 1, gen_random_uuid(), seller_id, 'apartment', false, 0);

    INSERT INTO property.listing_revisions (
        id, listing_id, revision_no, edit_action_id, created_by_account_id,
        property_type, district, town, price_basis, entered_price, currency,
        price_area_unit, land_area, land_area_unit, land_area_approximate, vehicle_access
    )
    VALUES (
        land_revision_id, land_id, 1, gen_random_uuid(), seller_id,
        'land', 'Example District', 'Example Town', 'per_unit', 250000, 'LKR',
        'perch', 0.125, 'acre', true, true
    );

    UPDATE property.listings AS listing
    SET current_draft_revision_id = draft.revision_id
    FROM (VALUES (house_id, house_revision_id),
                 (apartment_id, apartment_revision_id),
                 (land_id, land_revision_id)) AS draft(listing_id, revision_id)
    WHERE listing.id = draft.listing_id;

    -- A synthetic ciphertext placeholder represents the required private phone slot.
    INSERT INTO property.private_details (
        id, listing_id, detail_kind, slot_no, encrypted_value, encryption_key_ref
    )
    VALUES (gen_random_uuid(), land_id, 'phone', 1, decode('010203', 'hex'), 'fixture-key');

    INSERT INTO property.showcase_revisions (
        id, listing_id, source_revision_id, action_id, headline, description
    )
    VALUES (
        showcase_id, land_id, land_revision_id, gen_random_uuid(),
        'Example Town Plot', 'Fictional land listing for disposable database tests.'
    );

    UPDATE property.listings SET current_showcase_id = showcase_id WHERE id = land_id;

    INSERT INTO property.publications (
        id, listing_id, listing_revision_id, showcase_id, published_by, action_id
    )
    VALUES (publication_id, land_id, land_revision_id, showcase_id, seller_id, gen_random_uuid());

    INSERT INTO property.current_publications (listing_id, publication_id)
    VALUES (land_id, publication_id);
END
$$;
