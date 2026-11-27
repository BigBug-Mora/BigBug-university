import os
import unittest
from uuid import UUID, uuid4
from unittest.mock import patch

import psycopg
from fastapi import HTTPException
from fastapi.testclient import TestClient

from project.services.property.actor import Actor
from project.services.property.app import build_app


class FixtureActor:
    def require(self, request, callers):
        seller = request.headers.get("x-fixture-actor")
        if not seller:
            raise HTTPException(401)
        return Actor(UUID(seller))


class StoreCase(unittest.TestCase):
    def setUp(self):
        url = os.environ["ESTATEFLOW_TEST_PROPERTY_DATABASE_URL"]
        self.enterContext(patch.dict(os.environ, ESTATEFLOW_PROPERTY_DATABASE_URL=url))
        self.db = self.enterContext(psycopg.connect(url, autocommit=True))
        self.client = self.enterContext(TestClient(build_app(FixtureActor())))
        self.owner = {"x-fixture-actor": str(uuid4())}
        self.other = {"x-fixture-actor": str(uuid4())}

    def create(self, **fields):
        command = {"create_action_id": str(uuid4()), "draft": {"property_type": "house", **fields}}
        result = self.client.post("/listings", json=command, headers=self.owner)
        self.assertEqual(result.status_code, 200, result.text)
        return command, result.json()


class DraftTests(StoreCase):
    def test_role(self):
        version, role = self.db.execute("SELECT current_setting('server_version_num')::int,current_user").fetchone()
        self.assertEqual(version // 10000, 17)
        self.assertEqual(role, "estateflow_property")
        for query in ["CREATE TABLE property.unwanted (id int)", "SELECT * FROM account.accounts",
                      "SELECT * FROM engagement.disclosure_grants", "DELETE FROM property.listing_revisions"]:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                self.db.execute(query)

    def test_property_types_and_validation(self):
        for fields in [dict(property_type="house", house_storey_count=1),
                       dict(property_type="apartment", apartment_floor_no=0),
                       dict(property_type="land", price_basis="per_unit", entered_price=100,
                            currency="LKR", price_area_unit="perch")]:
            _, result = self.create(**fields)
            path = "/listings/" + result["listing_id"]
            self.assertEqual(self.client.get(path, headers=self.owner).json(), result)
        for invalid in [dict(property_type="land", bedroom_count=0), dict(parking_spaces=0, covered_parking_spaces=1),
                        dict(price_basis="per_unit", currency="LKR", entered_price=12, price_area_unit="acre")]:
            response = self.client.post("/listings", headers=self.owner, json={
                "create_action_id": str(uuid4()), "draft": {"property_type": "house", **invalid}})
            self.assertEqual(response.status_code, 422)
        self.assertEqual(len(self.client.get("/listings", headers=self.owner).json()), 3)

    def test_revision_replay_and_ownership(self):
        command, first = self.create(bedroom_count=0, vehicle_access=False, land_area="1.25", land_area_unit="acre",
                                     land_area_approximate=True, standard_fact_evidence={"bedroom_count":{"source_kind":"seller"}},
                                     access_road_width={"number_value":12,"unit":"ft","approximate":True})
        path = "/listings/" + first["listing_id"]
        self.assertEqual(first["revision"]["bedroom_count"], 0)
        self.assertIs(first["revision"]["vehicle_access"], False)
        self.assertIsNone(first["revision"]["parking_spaces"])
        edit = {"edit_action_id": str(uuid4()), "parent_revision_id": first["revision"]["id"],
                "draft": {**command["draft"], "town": "Fictional town"}}
        def save(payload, headers):
            return self.client.post(path + "/revisions", headers=headers, json=payload)
        second = save(edit, self.owner).json()
        self.assertEqual(second["revision"]["revision_no"], 2)
        self.assertEqual(second["facts"], first["facts"])
        self.assertEqual(save(edit,self.owner).json(), second)
        self.assertEqual(self.client.post("/listings",headers=self.owner,json=command).json(), first)
        self.assertEqual(save({**edit, "edit_action_id":str(uuid4())},self.owner).status_code, 409)
        self.assertEqual(self.client.get(path,headers=self.owner).json(), second)
        self.assertEqual(self.client.get("/listings", headers=self.other).json(), [])
        for headers, status in [(self.other,404), ({},401)]:
            self.assertEqual(self.client.get(path,headers=headers).status_code, status)
            self.assertEqual(save(edit,headers).status_code, status)
        self.assertEqual(self.client.post("/listings",json=command).status_code,401)
        self.assertEqual(self.client.get("/listings").status_code,401)
