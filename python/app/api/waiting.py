from __future__ import annotations

from fastapi import APIRouter, Query

from ..db import exec_one, fetch_all, fetch_one, tx
from ..response import vo
from .common import token_verify_member

router = APIRouter(prefix="/api/waiting", tags=["waiting"])


@router.post("/waitCreate")
def wait_create(token: str = Query(""), action_id: int = Query(...), borrow: bool = Query(False)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        if int(user.get("state") or 0) != 2:
            return vo(-1, "Identify Incorrect")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action or int(action.get("state") or 0) != 2:
            return vo(0, "No Action")

        members = fetch_one(conn, "select count(*) as c from records where action_id=:aid", {"aid": action_id})
        if members and int(members["c"]) < int(action.get("max_num") or 0):
            return vo(1, "Not Full")

        in_action = fetch_one(
            conn,
            "select count(*) as c from records where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
        )
        in_wait = fetch_one(
            conn,
            "select count(*) as c from waiting where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
        )
        if (in_action and int(in_action["c"]) > 0) or (in_wait and int(in_wait["c"]) != 0):
            return vo(2, "Repeated")

        rank_row = fetch_one(conn, "select count(*) as c from waiting where action_id=:aid", {"aid": action_id})
        rank = int(rank_row["c"]) + 1 if rank_row else 1

        exec_one(
            conn,
            "insert into waiting (user_id, action_id, `rank`, borrow) values (:uid, :aid, :rank, :borrow)",
            {"uid": user["id"], "aid": action_id, "rank": rank, "borrow": int(borrow)},
        )
        return vo(3, "Successful")


@router.post("/waitDelete")
def wait_delete(token: str = Query(""), waiting_id: int = Query(...)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        wait = fetch_one(conn, "select * from waiting where ID=:id", {"id": waiting_id})
        if not wait:
            return vo(-1, "No Waiting")

        if int(wait.get("user_id") or 0) != int(user["id"]):
            return vo(0, "User Not Match")

        exec_one(
            conn,
            "update waiting set `rank` = `rank`-1 where action_id=:aid and `rank`>=:con_rank",
            {"aid": wait["action_id"], "con_rank": wait["rank"]},
        )
        exec_one(conn, "delete from waiting where ID=:id", {"id": waiting_id})
        return vo(1, "Delete Successful")


@router.post("/queryWaiting")
def query_waiting(token: str = Query("")):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(status)

        rows = fetch_all(conn, "select * from waiting_view where user_id=:uid", {"uid": user["id"]})
        return vo(1, rows)
