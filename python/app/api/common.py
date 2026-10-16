from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.engine import Connection

from ..db import exec_one, fetch_one, sql_binary
from ..passwords import verify_user_password
from ..utils import new_token, parse_maybe_datetime


def token_verify_member(conn: Connection, token: str) -> tuple[int, dict | None]:
    # Returns (status, user_view)
    if not token:
        return -1, None

    exists = fetch_one(conn, "select count(*) as c from tokens where tokens.token=:token", {"token": token})
    if not exists or int(exists["c"]) == 0:
        return -1, None

    token_row = fetch_one(conn, "select * from tokens where tokens.token=:token", {"token": token})
    if not token_row:
        return -1, None

    now = datetime.now()
    raw_expiry = token_row.get("out_time")
    expiry = parse_maybe_datetime(raw_expiry)
    if expiry is None or expiry < now:
        exec_one(conn, "delete from tokens where token=:token", {"token": token})
        return 0, None

    user = fetch_one(conn, "select * from user_view where ID=:user_id", {"user_id": token_row["user_id"]})
    if not user or user.get("state") is None or int(user["state"]) <= 0 or int(user["state"]) > 3:
        exec_one(conn, "delete from tokens where token=:token", {"token": token})
        return 0, None

    return 1, user


def token_verify_admin(conn: Connection, token: str) -> tuple[int, dict | None]:
    if not token:
        return -1, None

    exists = fetch_one(conn, "select count(*) as c from tokens where tokens.token=:token", {"token": token})
    if not exists or int(exists["c"]) == 0:
        return -1, None

    token_row = fetch_one(conn, "select * from tokens where tokens.token=:token", {"token": token})
    if not token_row:
        return -1, None

    now = datetime.now()
    raw_expiry = token_row.get("out_time")
    expiry = parse_maybe_datetime(raw_expiry)
    if expiry is None or expiry < now:
        exec_one(conn, "delete from tokens where token=:token", {"token": token})
        return 0, None

    user = fetch_one(conn, "select * from user_view where ID=:user_id", {"user_id": token_row["user_id"]})
    if not user or user.get("state") is None or int(user["state"]) <= 3:
        exec_one(conn, "delete from tokens where token=:token", {"token": token})
        return 0, None

    return 1, user


def login_common(conn: Connection, username: str, password: str, *, admin: bool) -> tuple[int, str | None]:
    user = fetch_one(conn, f"select * from users where {sql_binary('username')}=:username", {"username": username})
    if not user:
        return -2, None
    if not verify_user_password(conn, user, password):
        return -2, None

    state = int(user.get("state") or 0)
    if admin:
        if state < 4:
            return -1, None
        # success status is 0 in AdminLoginController
        token_value = new_token()
        out_time = datetime.now() + timedelta(hours=3)
        exec_one(conn, "delete from tokens where user_id=:uid", {"uid": user["id"]})
        exec_one(
            conn,
            "insert into tokens(user_id, token, out_time) values (:uid, :token, :out_time)",
            {"uid": user["id"], "token": token_value, "out_time": out_time},
        )
        return 0, token_value

    # member/staff login
    if state <= 0 or state > 3:
        return state, None

    token_value = new_token()
    out_time = datetime.now() + timedelta(hours=3)
    exec_one(conn, "delete from tokens where user_id=:uid", {"uid": user["id"]})
    exec_one(
        conn,
        "insert into tokens(user_id, token, out_time) values (:uid, :token, :out_time)",
        {"uid": user["id"], "token": token_value, "out_time": out_time},
    )
    return state, token_value
