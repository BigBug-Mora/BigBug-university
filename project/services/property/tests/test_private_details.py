import json
import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from cryptography.fernet import Fernet
from fastapi import HTTPException

from project.services.property.private_details import KeyRing
from test_drafts import StoreCase


def keys():
    return {
        "ESTATEFLOW_PRIVATE_DETAIL_KEYS": json.dumps(
            {ref: Fernet.generate_key().decode() for ref in ["a", "b"]}
        ),
        "ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF": "a",
    }


class EncryptionTests(unittest.TestCase):
    def test_rotation_binding_and_invalid_key(self):
        with patch.dict(os.environ, keys()):
            ring = KeyRing()
            detail = uuid4()
            row = {
                "id": detail,
                "encrypted_value": ring.encrypt(detail, "private"),
                "encryption_key_ref": "a",
            }
            os.environ["ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF"] = "b"
            self.assertEqual(KeyRing().decrypt(row), "private")
            with self.assertRaises(HTTPException):
                KeyRing().decrypt({**row, "id": uuid4()})
            os.environ["ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF"] = "missing"
            with self.assertRaises(HTTPException):
                KeyRing()


class PrivateTests(StoreCase):
    def test_slot_lifecycle_and_isolation(self):
        self.enterContext(patch.dict(os.environ, keys()))
        _, draft = self.create()
        listing = "/listings/" + draft["listing_id"]
        path = listing + "/private-details"

        def put(slot, value, headers=None):
            return self.client.put(
                path + "/" + slot,
                headers=self.owner if headers is None else headers,
                json={"value": value},
            )

        old = put("phone/1", "+15550101111").json()["id"]
        for slot, value in [
            ("phone/2", "+15550102222"),
            ("phone/3", "+15550103333"),
            ("written_address/1", "Fictional Lane"),
            ("map_pin/1", {"latitude": 0, "longitude": 0}),
        ]:
            self.assertEqual(put(slot, value).status_code, 200)
        self.assertEqual(put("phone/1", "+1 555 010 2222").status_code, 409)
        self.assertEqual(put("map_pin/1", {"latitude": 0}).status_code, 422)
        self.assertEqual(put("phone/4", "+15550103333").status_code, 422)
        self.assertEqual(put("phone/1", "+15550104444").json()["id"], old)
        items = self.client.get(path, headers=self.owner).json()
        self.assertEqual(next(row["value"] for row in items if row["id"] == old), "+15550104444")
        self.assertNotIn("Fictional Lane", self.client.get(listing, headers=self.owner).text)
        value, ref = self.db.execute(
            "SELECT encrypted_value,encryption_key_ref FROM property.private_details WHERE id=%s", (old,)
        ).fetchone()
        self.assertNotIn(b"15550104444", value)
        self.assertEqual(ref, "a")
        for headers, status in [(self.other, 404), ({}, 401)]:
            self.assertEqual(self.client.get(path, headers=headers).status_code, status)
            self.assertEqual(put("phone/1", "+15550105555", headers).status_code, status)
            self.assertEqual(self.client.delete(path + "/" + old, headers=headers).status_code, status)
        self.assertEqual(self.client.delete(path + "/" + old, headers=self.owner).status_code, 204)
        self.assertNotEqual(put("phone/1", "+15550104444").json()["id"], old)
        retired = next(
            row for row in self.client.get(path, headers=self.owner).json() if row["id"] == old
        )
        self.assertIsNotNone(retired["retired_at"])
        self.assertNotIn("value", retired)
        self.assertEqual(
            self.db.execute(
                "SELECT encrypted_value,encryption_key_ref FROM property.private_details WHERE id=%s",
                (old,),
            ).fetchone(),
            (None, None),
        )
