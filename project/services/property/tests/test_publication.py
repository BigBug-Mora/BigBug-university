from decimal import Decimal
from uuid import uuid4

from test_showcase import ShowcaseCase


class PublicationTests(ShowcaseCase):
    def buyer(self, draft, headers=None):
        return self.client.get("/published-listings/" + draft["listing_id"],
                               headers=self.other if headers is None else headers)

    def test_auth_unpublished_missing_and_uuid_validation(self):
        _, draft = self.create()
        for headers, expected in [({}, 401), (self.owner, 404), (self.other, 404)]:
            response = self.buyer(draft, headers)
            self.assertEqual(response.status_code, expected)
            self.assertEqual(response.headers["cache-control"], "no-store")
        missing = self.buyer({"listing_id": str(uuid4())})
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json(), {"detail": "Listing unavailable"})
        malformed = self.buyer({"listing_id": "courtyard-house"})
        self.assertEqual(malformed.status_code, 422)
        self.assertEqual(malformed.headers["cache-control"], "no-store")

    def test_published_price_and_showcase_are_isolated_from_private_edits(self):
        command, first, path = self.ready(vehicle_access=False, parking_spaces=0)
        _, authored = self.author(first)
        self.assertEqual(self.publish(first, authored).status_code, 200)
        original = self.buyer(first)
        self.assertEqual(original.status_code, 200, original.text)
        self.assertEqual(original.headers["cache-control"], "no-store")
        body = original.json()
        self.assertEqual(body["entered_price"], "100000.00")
        self.assertEqual(body["total_asking_price"], "100000.00")
        self.assertIs(body["vehicle_access"], False)
        self.assertEqual(body["parking_spaces"], 0)
        self.assertIsNone(body["covered_parking_spaces"])
        self.assertEqual(body["gallery_photos"], [])
        self.assertEqual(body["featured_photos"], [])
        for private in ("seller_account_id", "created_by_account_id", "edit_action_id", "action_id",
                        "current_draft_revision_id", "current_showcase_id", "private_details", "encrypted_value"):
            self.assertNotIn(private, original.text)
        self.assertNotIn("15550101111", original.text)
        second = self.edit(path, first, command["draft"] | {"entered_price": "987654.32"})
        _, newer = self.author(second, authored["id"])
        self.assertEqual(self.buyer(first).json(), body)
        self.assertEqual(self.publish(second, authored).status_code, 409)
        self.assertEqual(self.buyer(first).json(), body)
        self.assertEqual(self.publish(second, newer).status_code, 200)
        result = self.buyer(first).json()
        self.assertEqual(result["entered_price"], "987654.32")
        self.assertEqual(result["revision_no"], 2)
        self.assertEqual(result["showcase_id"], newer["id"])

    def test_public_approval_is_frozen_and_chat_override_does_not_change_page(self):
        command, first, path = self.ready(access_road_width={"number_value": "15", "unit": "ft", "approximate": True},
                                          access_road_width_approved_for_public=True)
        _, authored = self.author(first)
        self.assertEqual(self.publish(first, authored).status_code, 200)
        original = self.buyer(first).json()
        self.assertEqual(original["facts"][0]["number_value"], "15")
        self.assertEqual(original["facts"][0]["display_name"], "Access road width")
        self.assertIs(original["facts"][0]["approximate"], True)
        second = self.edit(path, first, command["draft"] | {
            "access_road_width": {"number_value": "14", "unit": "ft"},
            "access_road_width_approved_for_public": False,
        })
        self.db.execute("UPDATE property.buyer_visible_facts SET fact_version_id=%s WHERE listing_id=%s",
                        (second["facts"][0]["id"], first["listing_id"]))
        self.assertEqual(self.buyer(first).json(), original)
        _, authored = self.author(second, authored["id"])
        self.assertEqual(self.publish(second, authored).status_code, 200)
        self.assertEqual(self.buyer(first).json()["facts"], [])

    def test_per_unit_land_price_converts_units_and_preserves_precision(self):
        _, land, _ = self.ready(property_type="land", bedroom_count=None, bathroom_count=None,
                                price_basis="per_unit", entered_price="250000", price_area_unit="perch",
                                land_area="0.125", land_area_unit="acre", land_area_approximate=True)
        _, authored = self.author(land)
        self.assertEqual(self.publish(land, authored).status_code, 200)
        result = self.buyer(land).json()
        self.assertEqual(result["price_basis"], "per_unit")
        self.assertEqual(result["price_area_unit"], "perch")
        self.assertEqual(result["entered_price"], "250000.00")
        self.assertEqual(Decimal(result["total_asking_price"]), Decimal("5000000.00"))
        self.assertIs(result["total_derived_from_approximate_area"], True)

    def test_incomplete_publication_is_422_and_leaves_buyer_unavailable(self):
        _, draft = self.create()
        _, authored = self.author(draft)
        self.assertEqual(self.publish(draft, authored).status_code, 422)
        self.assertEqual(self.buyer(draft).status_code, 404)
