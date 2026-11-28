from decimal import Decimal
from uuid import uuid4

import psycopg

from test_showcase import ShowcaseCase


class SearchCase(ShowcaseCase):
    """Independent published fixtures, created through the owning HTTP operations."""

    def setUp(self):
        super().setUp()
        self.tag = "Search-" + str(uuid4())

    def listing(self, kind, access, *, publish=True, **changes):
        fields = dict(property_type=kind, district=self.tag, town=self.tag + " " + kind,
                      vehicle_access=access, entered_price="2000000", parking_spaces=0)
        if kind == "apartment":
            fields.update(land_area=None, land_area_unit=None, bedroom_count=None, bathroom_count=None,
                          floor_area="100", floor_area_unit="sq_m", entered_price="3000000")
        elif kind == "land":
            fields.update(bedroom_count=None, bathroom_count=None, price_basis="per_unit",
                          price_area_unit="perch", entered_price="250000", land_area="0.125",
                          land_area_unit="acre", land_area_approximate=True)
        else:
            fields.update(town=self.tag + " 100%_! Courtyard", floor_area="1000", floor_area_unit="sq_ft",
                          bedroom_count=0, bathroom_count=1)
        command, draft, path = self.ready(**(fields | changes))
        authored = None
        if publish:
            _, authored = self.author(draft)
            response = self.publish(draft, authored)
            self.assertEqual(response.status_code, 200, response.text)
        return command, draft, path, authored

    def trio(self):
        return {kind: self.listing(kind, access) for kind, access in
                (("land", True), ("house", False), ("apartment", None))}

    def query(self, **filters):
        response = self.client.get("/published-listings", headers=self.other,
                                   params={"district": self.tag, **filters})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        return response.json()

    def ids(self, **filters):
        return {row["listing_id"] for row in self.query(**filters)["items"]}


class SearchTests(SearchCase):
    def test_types_location_case_and_literal_wildcards(self):
        fixtures = self.trio()
        self.assertEqual(self.query()["total"], 3)
        for kind, (_, draft, _, _) in fixtures.items():
            self.assertEqual(self.ids(property_type=kind), {draft["listing_id"]})
        self.assertEqual(self.query(district=self.tag.upper(), town=self.tag.lower())["total"], 3)
        self.assertEqual(self.ids(town="100%_!"), {fixtures["house"][1]["listing_id"]})
        for literal in (self.tag + "%", self.tag + "_", "' OR TRUE --", "\\"):
            self.assertEqual(self.query(town=literal)["total"], 0)

    def test_vehicle_modes_and_confirmed_first_order(self):
        fixtures = self.trio()
        all_items = self.query(vehicle_access="any")["items"]
        self.assertEqual({row["vehicle_access_status"] for row in all_items}, {"confirmed", "false", "unknown"})
        self.assertTrue(all(row["match_status"] == "matched" for row in all_items))
        required = self.query(vehicle_access="required")["items"]
        self.assertEqual([row["listing_id"] for row in required],
                         [fixtures["land"][1]["listing_id"], fixtures["apartment"][1]["listing_id"]])
        self.assertEqual([row["match_status"] for row in required], ["matched", "needs_confirmation"])
        self.assertEqual([row["vehicle_access"] for row in required], [True, None])
        self.assertEqual(self.ids(vehicle_access="confirmed"), {fixtures["land"][1]["listing_id"]})
        self.assertEqual(self.ids(vehicle_access="none"), {fixtures["house"][1]["listing_id"]})

    def test_budget_uses_calculated_total_and_scopes_currency(self):
        _, land, _, _ = self.listing("land", True)
        result = self.query(property_type="land", currency="LKR", max_price="5500000")["items"][0]
        self.assertEqual(result["listing_id"], land["listing_id"])
        self.assertEqual(result["entered_price"], "250000.00")
        self.assertEqual(result["total_asking_price"], "5000000.00")
        self.assertIs(result["total_derived_from_approximate_area"], True)
        for bounds in ({"max_price": "4500000"}, {"min_price": "5500000"}):
            self.assertEqual(self.query(currency="LKR", **bounds)["total"], 0)
        self.assertEqual(self.query(currency="LKR", min_price="5000000", max_price="5000000")["total"], 1)
        _, usd, _, _ = self.listing("land", True, currency="USD", price_basis="total", price_area_unit=None,
                                      entered_price="5000000")
        self.assertEqual(self.ids(currency="LKR"), {land["listing_id"]})
        self.assertEqual(self.ids(currency="USD", max_price="5000000"), {usd["listing_id"]})

    def test_per_unit_pricing_for_all_area_units(self):
        cases = (("perch", "250000", "5000000.00"), ("acre", "40000000", "5000000.00"),
                 ("hectare", "10000000", "505857.05"), ("sq_m", "10000", "5058570.53"),
                 ("sq_ft", "1000", "5445000.00"))
        for unit, entered, expected in cases:
            with self.subTest(unit=unit):
                town = self.tag + " " + unit
                _, draft, _, _ = self.listing("land", True, town=town, price_area_unit=unit, entered_price=entered)
                exact = self.query(town=town, currency="LKR", min_price=expected, max_price=expected)
                self.assertEqual(exact["total"], 1)
                self.assertEqual(exact["items"][0]["listing_id"], draft["listing_id"])
                self.assertEqual(exact["items"][0]["total_asking_price"], expected)
                below = str(Decimal(expected) - Decimal("0.01"))
                self.assertEqual(self.query(town=town, currency="LKR", max_price=below)["total"], 0)

    def test_cross_unit_land_and_floor_area_minima(self):
        fixtures = self.trio()
        for unit, value in (("perch", "20"), ("acre", "0.125"), ("hectare", "0.05058570528"),
                            ("sq_m", "505.8570528"), ("sq_ft", "5445")):
            with self.subTest(unit=unit):
                self.assertEqual(self.ids(property_type="land", min_land_area=value, land_area_unit=unit),
                                 {fixtures["land"][1]["listing_id"]})
                above = str(Decimal(value) + Decimal("0.000000000001"))
                self.assertEqual(self.query(property_type="land", min_land_area=above, land_area_unit=unit)["total"], 0)
        self.assertEqual(self.ids(min_floor_area="95", floor_area_unit="sq_m"),
                         {fixtures["apartment"][1]["listing_id"]})
        self.assertEqual(self.ids(min_floor_area="1050", floor_area_unit="sq_ft"),
                         {fixtures["apartment"][1]["listing_id"]})
        self.assertEqual(self.query(min_floor_area="1000", floor_area_unit="sq_ft")["total"], 2)

    def test_zero_counts_remain_distinct_from_unknown(self):
        fixtures = self.trio()
        items = {item["property_type"]: item for item in self.query()["items"]}
        self.assertEqual(items["house"]["bedroom_count"], 0)
        self.assertIsNone(items["apartment"]["bedroom_count"])
        self.assertIsNone(items["land"]["bedroom_count"])
        house_id = fixtures["house"][1]["listing_id"]
        self.assertEqual(self.ids(min_bedrooms=0, min_bathrooms=0), {house_id})
        self.assertEqual(self.query(min_bedrooms=1)["total"], 0)
        self.assertEqual(self.query(min_bathrooms=2)["total"], 0)

    def test_draft_price_and_private_details_stay_out_until_republication(self):
        command, house, path, authored = self.listing("house", False)
        _, draft, _, _ = self.listing("house", None, publish=False)
        for endpoint, value in (("written_address/1", "Secret Search Lane"),
                                ("map_pin/1", {"latitude": "6.123456", "longitude": "80.123456"})):
            self.assertEqual(self.client.put(path + "/private-details/" + endpoint, headers=self.owner,
                                             json={"value": value}).status_code, 200)
        before = self.query()
        self.assertEqual(before["total"], 1)
        self.assertNotIn(draft["listing_id"], str(before))
        changed = self.edit(path, house, command["draft"] | {"entered_price": "9876543.21"})
        self.assertEqual(self.query(), before)
        for secret in ("15550101111", "Secret Search Lane", "6.123456", "80.123456", "private_details",
                       "encrypted_value", "written_address", "map_pin", "seller_account_id", "current_draft_revision_id"):
            self.assertNotIn(secret, str(before))
        self.assertEqual(self.client.get(path + "/private-details", headers=self.other).status_code, 404)
        _, newer = self.author(changed, authored["id"])
        response = self.publish(changed, newer)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.query()["items"][0]["entered_price"], "9876543.21")

    def test_pagination_order_totals_and_empty_pages(self):
        self.trio()
        all_items = self.query()["items"]
        self.assertEqual([item["published_at"] for item in all_items],
                         sorted((item["published_at"] for item in all_items), reverse=True))
        collected = []
        for offset in range(3):
            page = self.query(limit=1, offset=offset)
            self.assertEqual((page["total"], page["limit"], page["offset"]), (3, 1, offset))
            collected.extend(page["items"])
        self.assertEqual(collected, all_items)
        self.assertEqual(self.query(limit=1, offset=20)["items"], [])
        self.assertEqual(self.query(offset=20)["total"], 3)
        empty = self.query(town="not-present")
        self.assertEqual((empty["items"], empty["total"]), ([], 0))

    def test_auth_validation_and_runtime_reference_privileges(self):
        version, role = self.db.execute("SELECT current_setting('server_version_num')::int,current_user").fetchone()
        self.assertEqual((version // 10000, role), (17, "estateflow_property"))
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            self.db.execute("UPDATE property.area_units SET square_metres=2 WHERE code='sq_m'")
        unauthorized = self.client.get("/published-listings")
        self.assertEqual(unauthorized.status_code, 401)
        self.assertEqual(unauthorized.headers["cache-control"], "no-store")
        for params in ({"property_type": "villa"}, {"min_price": "10"}, {"currency": "lkr"},
                       {"currency": "LKR", "max_price": "0"}, {"min_bedrooms": "-1"},
                       {"min_bathrooms": "1.5"}, {"vehicle_access": "true"}, {"limit": "0"},
                       {"limit": "51"}, {"offset": "-1"}, {"min_land_area": "1"},
                       {"min_floor_area": "1", "floor_area_unit": "acre"}, {"private_details": "1"}):
            with self.subTest(params=params):
                response = self.client.get("/published-listings", params=params, headers=self.other)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(response.headers["cache-control"], "no-store")
