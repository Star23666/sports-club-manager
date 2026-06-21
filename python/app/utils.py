from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime

SALT = "$0q#Ag%#0xN9+KuB"  # must match Java MD5Util


PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$")


def encrypt_md5(input_str: str) -> str:
    # Re-implement backend-system MD5Util.encryptMD5 exactly.
    mixed = "".join(ch + SALT[i % 16] for i, ch in enumerate(input_str))
    return hashlib.md5(mixed.encode("utf-8")).hexdigest()


def new_token() -> str:
    return str(uuid.uuid4())


def parse_maybe_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.strip()
    if not s:
        return None

    # Layui date-picker may provide ISO strings; admin UI also converts to "YYYY-MM-DD HH:MM:SS".
    # Support both.
    try:
        # Handle trailing Z
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
        return datetime.fromisoformat(s)
    except Exception:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue

    return None


def mask_equip_id(equip_id_md5: str) -> str:
    if equip_id_md5 is None:
        return ""
    s = str(equip_id_md5)
    if len(s) <= 6:
        return s
    return s[:3] + "******" + s[-3:]
