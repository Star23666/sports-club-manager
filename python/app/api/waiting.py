from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from .auth_transport import bearer_token

from ..db import exec_one, fetch_all, fetch_one, lock_action, tx
from ..response import vo
from .common import token_verify_member

router = APIRouter(prefix="/api/waiting", tags=["waiting"])


@router.post("/waitCreate")
def wait_create(token: str = Depends(bearer_token), action_id: int = Query(...), borrow: bool = Query(False)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        if int(user.get("state") or 0) != 2:
            return vo(-1, "Identify Incorrect")

        action = lock_action(conn, action_id)
        if not action or int(action.get("state") or 0) != 2:
            return vo(0, "No Action")

        members = fetch_all(conn, "select ID from records where action_id=:aid", {"aid": action_id}, for_update=True)
        if len(members) < int(action.get("max_num") or 0):
            return vo(1, "Not Full")

        in_action = fetch_all(
            conn,
            "select ID from records where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
            for_update=True,
        )
        in_wait = fetch_all(
            conn,
            "select ID from waiting where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
            for_update=True,
        )
        if in_action or in_wait:
            return vo(2, "Repeated")

        rank = len(fetch_all(
            conn, "select ID from waiting where action_id=:aid", {"aid": action_id}, for_update=True,
        )) + 1

        exec_one(
            conn,
            "insert into waiting (user_id, action_id, `rank`, borrow) values (:uid, :aid, :rank, :borrow)",
            {"uid": user["id"], "aid": action_id, "rank": rank, "borrow": int(borrow)},
        )
        return vo(3, "Successful")


@router.post("/waitDelete")
def wait_delete(token: str = Depends(bearer_token), waiting_id: int = Query(...)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        wait_ref = fetch_one(conn, "select action_id from waiting where ID=:id", {"id": waiting_id})
        if not wait_ref:
            return vo(-1, "No Waiting")

        lock_action(conn, wait_ref["action_id"])
        wait = fetch_one(conn, "select * from waiting where ID=:id", {"id": waiting_id}, for_update=True)
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
def query_waiting(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(status)

        rows = fetch_all(conn, "select * from waiting_view where user_id=:uid", {"uid": user["id"]})
        return vo(1, rows)
