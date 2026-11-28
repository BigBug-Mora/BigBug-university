import unittest

from pydantic import ValidationError

from project.services.property.models import SearchQuery
from test_drafts import StoreCase


class SearchQueryTests(unittest.TestCase):
    def test_related_filters_and_finite_numbers(self):
        for fields in (
            {"min_price": "10"}, {"currency": "lkr"},
            {"currency": "LKR", "min_price": "20", "max_price": "10"},
            {"min_land_area": "1"}, {"floor_area_unit": "sq_m"},
            {"min_floor_area": "1", "floor_area_unit": "acre"},
            {"max_price": "NaN", "currency": "LKR"}, {"min_land_area": "Infinity", "land_area_unit": "acre"},
            {"min_bedrooms": -1}, {"limit": 51}, {"offset": -1}, {"town": " "},
        ):
            with self.subTest(fields=fields), self.assertRaises(ValidationError):
                SearchQuery(**fields)


class SearchEndpointTests(StoreCase):
    def test_scoped_search_read_and_validation(self):
        # The original Phase 1 public land fixture remains untouched.
        response = self.client.get("/published-listings", headers=self.other, params={
            "town": "example town", "currency": "LKR", "max_price": "5000000",
            "min_land_area": "20", "land_area_unit": "perch", "vehicle_access": "confirmed",
        })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        result = response.json()
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["total_asking_price"], "5000000.00")
        self.assertEqual(result["items"][0]["vehicle_access_status"], "confirmed")
        self.assertEqual(result["items"][0]["match_status"], "matched")
        self.assertIsNone(result["items"][0]["cover_photo"])
        beyond = self.client.get("/published-listings", headers=self.other,
                                  params={"town": "example town", "offset": 50}).json()
        self.assertEqual(beyond["total"], 1)
        self.assertEqual(beyond["items"], [])
        for params, headers, expected in (({}, {}, 401), ({"min_price": "1"}, self.owner, 422),
                                          ({"vehicle_access": "invalid"}, self.owner, 422)):
            invalid = self.client.get("/published-listings", headers=headers, params=params)
            self.assertEqual(invalid.status_code, expected, invalid.text)
            self.assertEqual(invalid.headers["cache-control"], "no-store")
