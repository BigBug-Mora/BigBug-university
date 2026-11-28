import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import UUID, uuid4

import psycopg

from test_drafts import StoreCase
from test_private_details import keys


class ShowcaseCase(StoreCase):
    def setUp(self):
        super().setUp()
        self.enterContext(patch.dict(os.environ, keys()))

    def ready(self, **changes):
        fields = dict(town="Fictional town", district="Fictional district", price_basis="total",
                      entered_price="100000", currency="LKR", land_area="12", land_area_unit="perch",
                      bedroom_count=0, bathroom_count=0)
        command, draft = self.create(**(fields | changes))
        path = "/listings/" + draft["listing_id"]
        response = self.client.put(path + "/private-details/phone/1", headers=self.owner,
                                   json={"value": "+15550101111"})
        self.assertEqual(response.status_code, 200, response.text)
        return command, draft, path

    def author(self, draft, parent=None):
        command = dict(action_id=str(uuid4()), source_revision_id=draft["revision"]["id"],
                       parent_showcase_id=parent, headline="A considered home",
                       description="Seller-authored description.", highlights=["A quiet setting"])
        path = "/listings/" + draft["listing_id"] + "/showcases"
        result = self.client.post(path, headers=self.owner, json=command)
        self.assertEqual(result.status_code, 200, result.text)
        return command, result.json()

    def publish(self, draft, authored, action=None):
        return self.client.post("/listings/" + draft["listing_id"] + "/publish", headers=self.owner,
                                json=dict(action_id=action or str(uuid4()),
                                          listing_revision_id=draft["revision"]["id"], showcase_id=authored["id"]))

    def edit(self, path, draft, fields):
        result = self.client.post(path + "/revisions", headers=self.owner,
                                  json=dict(edit_action_id=str(uuid4()), parent_revision_id=draft["revision"]["id"],
                                            draft=fields))
        self.assertEqual(result.status_code, 200, result.text)
        return result.json()


class ShowcaseTests(ShowcaseCase):
    def test_author_preview_replay_ownership_and_validation(self):
        command, first, path = self.ready()
        action, authored = self.author(first)
        self.assertIsNone(authored["source_job_id"])
        self.assertEqual(self.client.post(path + "/showcases", headers=self.owner, json=action).json(), authored)
        preview = self.client.get(path + "/showcase", headers=self.owner)
        self.assertEqual(preview.headers["cache-control"], "no-store")
        self.assertEqual(preview.json()["missing_requirements"], [])
        self.assertTrue(preview.json()["showcase_matches_draft"])
        for headers, status in [(self.other, 404), ({}, 401)]:
            self.assertEqual(self.client.get(path + "/showcase", headers=headers).status_code, status)
            self.assertEqual(self.client.post(path + "/showcases", headers=headers, json=action).status_code, status)
            self.assertEqual(self.client.post(path + "/publish", headers=headers, json={
                "action_id": str(uuid4()), "listing_revision_id": first["revision"]["id"],
                "showcase_id": authored["id"],
            }).status_code, status)
        for invalid in [{"headline": " "}, {"highlights": []}, {"highlights": [" "]}]:
            self.assertEqual(self.client.post(path + "/showcases", headers=self.owner,
                                             json=action | invalid).status_code, 422)
        second = self.edit(path, first, command["draft"] | {"town": "Another town"})
        self.assertEqual(self.client.post(path + "/showcases", headers=self.owner,
                                         json=action | {"action_id": str(uuid4())}).status_code, 409)
        self.assertFalse(self.client.get(path + "/showcase", headers=self.owner).json()["showcase_matches_draft"])
        self.assertEqual(self.publish(second, authored).status_code, 409)

    def test_minimum_fields_each_type_and_phone_guard(self):
        for kind in ("house", "apartment", "land"):
            with self.subTest(kind=kind):
                _, draft = self.create(property_type=kind)
                _, authored = self.author(draft)
                self.assertEqual(self.publish(draft, authored).status_code, 422)
                fields = dict(property_type=kind, town="Town", district="District", price_basis="total",
                              entered_price="500", currency="LKR")
                fields |= ({"floor_area": "90", "floor_area_unit": "sq_m"} if kind == "apartment"
                           else {"land_area": "10", "land_area_unit": "perch"})
                if kind == "house":
                    fields |= dict(bedroom_count=0, bathroom_count=0)
                path = "/listings/" + draft["listing_id"]
                draft = self.edit(path, draft, fields)
                _, authored = self.author(draft, authored["id"])
                self.assertEqual(self.publish(draft, authored).status_code, 422)
                phone = self.client.put(path + "/private-details/phone/1", headers=self.owner,
                                        json={"value": "+15550101111"}).json()["id"]
                result = self.publish(draft, authored)
                self.assertEqual(result.status_code, 200, result.text)
                self.assertEqual(self.client.delete(path + "/private-details/" + phone, headers=self.owner).status_code, 422)

    def test_publish_replay_does_not_move_later_pointer_and_summary(self):
        command, first, path = self.ready()
        _, authored = self.author(first)
        action = str(uuid4())
        original = self.publish(first, authored, action)
        self.assertEqual(original.status_code, 200, original.text)
        second = self.edit(path, first, command["draft"] | {"entered_price": "200000"})
        self.assertEqual(self.publish(second, authored).status_code, 409)
        _, newer = self.author(second, authored["id"])
        latest = self.publish(second, newer)
        self.assertEqual(latest.status_code, 200, latest.text)
        self.assertEqual(self.publish(first, authored, action).json(), original.json())
        self.assertEqual(self.client.get(path + "/showcase", headers=self.owner).json()["publication"], latest.json())
        item = self.client.get("/listings", headers=self.owner).json()[0]
        self.assertEqual(item["published_revision_no"], 2)
        self.assertIsNotNone(item["published_at"])

    def test_approval_versions_and_reconciliation(self):
        command, draft, path = self.ready(access_road_width={"number_value": "15", "unit": "ft"},
                                          access_road_width_approved_for_public=True)
        _, authored = self.author(draft)
        self.assertEqual(self.publish(draft, authored).status_code, 200)
        old = draft["facts"][0]["id"]
        # A privately saved correction can be independently shared in a later phase.
        changed = self.edit(path, draft, command["draft"] | {"access_road_width": {"number_value": "14", "unit": "ft"},
                                                               "access_road_width_approved_for_public": False})
        shared = changed["facts"][0]["id"]
        self.db.execute("UPDATE property.buyer_visible_facts SET fact_version_id=%s WHERE listing_id=%s",
                        (shared, draft["listing_id"]))
        hidden = self.edit(path, changed, command["draft"] | {"access_road_width_approved_for_public": False})
        _, authored = self.author(hidden, authored["id"])
        self.assertEqual(self.publish(hidden, authored).status_code, 200)
        self.assertEqual(self.db.execute("SELECT fact_version_id FROM property.buyer_visible_facts WHERE listing_id=%s",
                                        (draft["listing_id"],)).fetchone()[0], UUID(shared))
        approved = self.edit(path, hidden, command["draft"])
        _, authored = self.author(approved, authored["id"])
        self.assertEqual(self.publish(approved, authored).status_code, 200)
        self.assertNotEqual(old, shared)
        self.assertEqual(str(self.db.execute("SELECT fact_version_id FROM property.buyer_visible_facts WHERE listing_id=%s",
                                            (draft["listing_id"],)).fetchone()[0]), approved["facts"][0]["id"])

    def test_simultaneous_publish_replays_once(self):
        _, draft, _ = self.ready()
        _, authored = self.author(draft)
        action = str(uuid4())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.publish(draft, authored, action), range(2)))
        self.assertEqual([r.status_code for r in results], [200, 200])
        self.assertEqual(results[0].json(), results[1].json())

    def test_approval_omission_preserves_exact_version_and_removal_clears_pointer(self):
        command, first, path = self.ready(access_road_width={"number_value": "15", "unit": "ft"},
                                          access_road_width_approved_for_public=True)
        _, authored = self.author(first)
        self.assertEqual(self.publish(first, authored).status_code, 200)
        fields = {k: v for k, v in command["draft"].items() if not k.startswith("access_road_width")}
        second = self.edit(path, first, fields)
        self.assertEqual(second["facts"], first["facts"])
        hidden = self.edit(path, second, fields | {"access_road_width_approved_for_public": False})
        self.assertFalse(hidden["facts"][0]["approved_for_public"])
        _, authored = self.author(hidden, authored["id"])
        self.assertEqual(self.publish(hidden, authored).status_code, 200)
        self.assertIsNone(self.db.execute("SELECT 1 FROM property.buyer_visible_facts WHERE listing_id=%s",
                                          (first["listing_id"],)).fetchone())

    def test_dedicated_override_preserved_for_unrelated_edit_then_superseded(self):
        command, first, path = self.ready(covered_parking_spaces=1, parking_spaces=3)
        _, authored = self.author(first)
        self.assertEqual(self.publish(first, authored).status_code, 200)
        correction = self.edit(path, first, command["draft"] | {"covered_parking_spaces": 2})
        self.db.execute(
            """INSERT INTO property.buyer_visible_facts (listing_id,fact_key,field_revision_id)
               VALUES (%s,'covered_parking_spaces',%s)""", (first["listing_id"], correction["revision"]["id"]),
        )
        unrelated = self.edit(path, correction, command["draft"] | {"entered_price": "200000"})
        _, authored = self.author(unrelated, authored["id"])
        self.assertEqual(self.publish(unrelated, authored).status_code, 200)
        self.assertIsNotNone(self.db.execute("SELECT 1 FROM property.buyer_visible_facts WHERE listing_id=%s",
                                             (first["listing_id"],)).fetchone())
        changed = self.edit(path, unrelated, command["draft"] | {"covered_parking_spaces": 3})
        _, authored = self.author(changed, authored["id"])
        self.assertEqual(self.publish(changed, authored).status_code, 200)
        self.assertIsNone(self.db.execute("SELECT 1 FROM property.buyer_visible_facts WHERE listing_id=%s",
                                          (first["listing_id"],)).fetchone())

    def test_publication_grants_are_minimal(self):
        for query in ["DELETE FROM property.publications", "UPDATE property.showcase_revisions SET headline='bad'",
                      "UPDATE property.listings SET seller_account_id=NULL", "SELECT * FROM agent.jobs",
                      "CREATE TABLE property.unwanted_publication (id int)"]:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                self.db.execute(query)

    def test_clearing_dedicated_value_only_removes_override_matching_outgoing_value(self):
        for shared_count in (1, 2):
            with self.subTest(shared_count=shared_count):
                command, first, path = self.ready(covered_parking_spaces=1, parking_spaces=3)
                _, authored = self.author(first)
                self.assertEqual(self.publish(first, authored).status_code, 200)
                shared = self.edit(path, first, command["draft"] | {"covered_parking_spaces": shared_count})
                self.db.execute(
                    """INSERT INTO property.buyer_visible_facts (listing_id,fact_key,field_revision_id)
                       VALUES (%s,'covered_parking_spaces',%s)""", (first["listing_id"], shared["revision"]["id"]),
                )
                cleared = self.edit(path, shared, command["draft"] | {"covered_parking_spaces": None})
                _, authored = self.author(cleared, authored["id"])
                self.assertEqual(self.publish(cleared, authored).status_code, 200)
                pointer = self.db.execute("SELECT 1 FROM property.buyer_visible_facts WHERE listing_id=%s",
                                           (first["listing_id"],)).fetchone()
                self.assertEqual(pointer is None, shared_count == 1)
