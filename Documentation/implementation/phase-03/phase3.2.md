# Phase 3.2 · Encrypted private details

Implement encrypted storage and management endpoints in the Property service for private phone numbers, written address, and GPS map pin under stable detail IDs.

[Phase 3](phase3.md) · [Property service](../../mvp/containers/property-service/property-service.md) · [Private details schema](../../mvp/database/schema.md#5-private-phone-numbers-written-address-and-gps-pin) · [Private disclosures contract](../../mvp/database/contracts.md#private-disclosures)

## Progress

- [x] Add an encryption module under `project/services/property/` using authenticated symmetric encryption (e.g., AES-GCM / Fernet via `cryptography`, already in the environment) with a configured key-reference map (`ESTATEFLOW_PRIVATE_DETAIL_KEYS` / `ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF`) so `encryption_key_ref` is stored alongside `encrypted_value` and supports key rotation. Never log plaintext private details or key material.
- [x] Implement seller private-detail endpoints behind `require_frontend_actor` with strict `seller_account_id == actor.account_id` checks:
  - `GET /listings/{listing_id}/private-details` — returns active private details for the owning seller (with `id`, `detail_kind`, `slot_no`, decrypted payload, `updated_at`) plus retired slot history metadata (without retired values).
  - `PUT /listings/{listing_id}/private-details/{detail_kind}/{slot_no}` (or structured upsert/edit endpoints) — validates `detail_kind` (`phone`, `written_address`, `map_pin`) and `slot_no` (`1..3` for `phone`, `1` for `written_address` and `map_pin`), enforces distinct active phone numbers per listing, and validates `map_pin` carries both latitude and longitude.
  - Editing an active slot updates `encrypted_value`, `encryption_key_ref`, and `updated_at` **in place**, preserving the same `id`.
  - `DELETE /listings/{listing_id}/private-details/{detail_id}` — clears `encrypted_value` and `encryption_key_ref` to `NULL` and sets `retired_at = now()`, permanently retiring that `id`.
  - Re-adding a detail in a previously retired slot inserts a new row with a **new** `id` (respecting the `UNIQUE (listing_id, detail_kind, slot_no, active_slot)` partial/generated constraint).
- [x] Ensure private details are never included in ordinary draft/public projections or error messages.
- [x] Add unit and PostgreSQL integration tests covering encryption/decryption round-trip, key-ref validation, distinct phone number enforcement, in-place edit preserving `id`, removal retiring `id`, re-add generating a new `id`, and cross-account denial.

## Acceptance check

Run the Property private-details unit and disposable PostgreSQL integration tests.

| Scenario | Expected result |
| --- | --- |
| Create phone (slots 1–3), written address, and map pin | Stored as non-empty `bytea` `encrypted_value` with `encryption_key_ref`; seller read decrypts accurately. |
| Duplicate active phone number on same listing | Rejected with `400`/`422` (or `409`) without overwriting existing slot. |
| Edit an existing private detail | Value updates in `property.private_details` and `id` remains unchanged. |
| Remove a private detail, then add a new one in the same slot | Original row has `retired_at IS NOT NULL`, `encrypted_value IS NULL`, `encryption_key_ref IS NULL`; new row gets a distinct `id`. |
| Different authenticated account | Denied (`403`/`404`) on read, write, and delete; no plaintext leaked in responses or logs. |

On 2026-11-28 all 12 Property tests passed against disposable PostgreSQL 17.6, including key rotation, authenticated detail identity, all five slots, duplicate denial, ciphertext inspection, retirement and cross-account denial. [Verification commands and revision](phase3.4.md#evidence)
