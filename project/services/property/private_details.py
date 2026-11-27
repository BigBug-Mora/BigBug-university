import json
import os
import re
from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Body, Depends, HTTPException

from .database import owned_listing, transaction


class KeyRing:
    def __init__(self):
        try:
            self.active = os.environ["ESTATEFLOW_PRIVATE_DETAIL_ACTIVE_KEY_REF"]
            keys = json.loads(os.environ["ESTATEFLOW_PRIVATE_DETAIL_KEYS"])
            self.keys = {ref: Fernet(key) for ref, key in keys.items()}
            if not self.active.strip() or self.active not in self.keys:
                raise ValueError
        except (AttributeError, KeyError, ValueError, TypeError):
            raise HTTPException(503, "Private detail keys unavailable") from None

    def encrypt(self, detail_id, value):
        payload = json.dumps([str(detail_id), value]).encode()
        return self.keys[self.active].encrypt(payload)

    def decrypt(self, row):
        try:
            payload = self.keys[row["encryption_key_ref"]].decrypt(bytes(row["encrypted_value"]))
            detail_id, value = json.loads(payload)
            if detail_id != str(row["id"]):
                raise ValueError
            return value
        except (KeyError, InvalidToken, ValueError):
            raise HTTPException(503, "Private detail unavailable") from None


def validate(kind, slot, value):
    if kind == "phone" and 1 <= slot <= 3 and isinstance(value, str):
        phone = re.sub(r"[\s().-]", "", value)
        if re.fullmatch(r"\+?[0-9]{7,15}", phone):
            return phone
    if kind == "written_address" and slot == 1 and isinstance(value, str) and 0 < len(value.strip()) <= 2000:
        return value.strip()
    if kind == "map_pin" and slot == 1 and isinstance(value, dict) and set(value) == {"latitude", "longitude"}:
        try:
            lat, lng = (Decimal(str(value[key])) for key in ("latitude", "longitude"))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return {"latitude": str(lat), "longitude": str(lng)}
        except (ValueError, InvalidOperation):
            pass
    raise HTTPException(422, "Check the private detail kind, slot and value.")


def private_routes(require_actor):
    router = APIRouter(prefix="/{listing_id}/private-details")
    actor = Depends(require_actor)

    @router.get("")
    def details(listing_id: UUID, seller=actor):
        with transaction() as db:
            owned_listing(db, listing_id, seller.account_id)
            rows = db.execute("""SELECT id,detail_kind,slot_no,updated_at,retired_at,encrypted_value,encryption_key_ref
                                 FROM property.private_details WHERE listing_id=%s ORDER BY detail_kind,slot_no,updated_at""",
                              (listing_id,)).fetchall()
            keys = KeyRing()
            for row in rows:
                if row["retired_at"] is None:
                    row["value"] = keys.decrypt(row)
                del row["encrypted_value"], row["encryption_key_ref"]
            return rows

    @router.put("/{kind}/{slot}")
    def put(listing_id: UUID, kind: str, slot: int, payload: dict = Body(), seller=actor):
        with transaction() as db:
            owned_listing(db, listing_id, seller.account_id, lock=True)
            value = validate(kind, slot, payload.get("value"))
            keys = KeyRing()
            active = db.execute("""SELECT id,slot_no,encrypted_value,encryption_key_ref FROM property.private_details
                                   WHERE listing_id=%s AND detail_kind=%s AND retired_at IS NULL""",
                                (listing_id, kind)).fetchall()
            existing = None
            for row in active:
                if row["slot_no"] == slot:
                    existing = row["id"]
                elif kind == "phone" and keys.decrypt(row) == value:
                    raise HTTPException(409, "This phone number already occupies another slot.")
            detail_id = existing or uuid4()
            encrypted = keys.encrypt(detail_id, value)
            if existing:
                db.execute("""UPDATE property.private_details SET encrypted_value=%s,encryption_key_ref=%s,
                              updated_at=now() WHERE id=%s""", (encrypted,keys.active,detail_id))
            else:
                db.execute("""INSERT INTO property.private_details
                              (id,listing_id,detail_kind,slot_no,encrypted_value,encryption_key_ref)
                              VALUES (%s,%s,%s,%s,%s,%s)""", (detail_id,listing_id,kind,slot,encrypted,keys.active))
            return {"id": detail_id}

    @router.delete("/{detail_id}", status_code=204)
    def retire(listing_id: UUID, detail_id: UUID, seller=actor):
        with transaction() as db:
            owned_listing(db, listing_id, seller.account_id, lock=True)
            row = db.execute("""UPDATE property.private_details SET encrypted_value=NULL,encryption_key_ref=NULL,
                                updated_at=coalesce(retired_at,now()),retired_at=coalesce(retired_at,now())
                                WHERE id=%s AND listing_id=%s RETURNING id""", (detail_id,listing_id)).fetchone()
            if not row:
                raise HTTPException(404, "Detail unavailable")

    return router
