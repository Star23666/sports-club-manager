"""Password hashing and transparent migration of legacy MD5 records."""

from __future__ import annotations

import hmac
import re

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy.engine import Connection

from .db import exec_one
from .utils import encrypt_md5

_hasher = PasswordHasher()
_LEGACY_MD5 = re.compile(r"^[0-9a-f]{32}$")
# The old database dump shipped this publicly known account. Never accept it.
LEGACY_DEFAULT_ADMIN_HASH = "e16a0b342f7858669d605b120684254c"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_user_password(conn: Connection, user: dict, password: str) -> bool:
    stored = str(user.get("password") or "")
    if stored.startswith("$argon2"):
        try:
            valid = _hasher.verify(stored, password)
        except (InvalidHashError, VerificationError):
            return False
        if valid and _hasher.check_needs_rehash(stored):
            exec_one(
                conn,
                "update users set password=:new where ID=:uid and password=:old",
                {"new": hash_password(password), "uid": user["id"], "old": stored},
            )
        return valid

    if not _LEGACY_MD5.fullmatch(stored):
        return False
    if int(user.get("state") or 0) >= 4 and stored == LEGACY_DEFAULT_ADMIN_HASH:
        return False
    if not hmac.compare_digest(stored, encrypt_md5(password)):
        return False

    # A successful legacy login upgrades the stored value in the same transaction.
    return exec_one(
        conn,
        "update users set password=:new where ID=:uid and password=:old",
        {"new": hash_password(password), "uid": user["id"], "old": stored},
    ) == 1
