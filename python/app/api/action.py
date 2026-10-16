from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from .auth_transport import bearer_token

from ..db import exec_one, fetch_all, fetch_one, lock_action, tx
from ..response import vo
from .common import token_verify_member

router = APIRouter(prefix="/api/action", tags=["action"])


def _action_to_dict(row: dict) -> dict:
    # Match Java Action fields (ignore borrow_num)
    keys = {
        "id",
        "title",
        "place",
        "time_range",
        "date",
        "max_num",
        "state",
        "open_time",
        "close_time",
        "staff_user_id",
        "wechat_url",
    }
    return {k: row.get(k) for k in keys}


@router.post("/queryAction")
def query_actions(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, _user = token_verify_member(conn, token)
        if status <= 0:
            return vo(status)

        rows = fetch_all(conn, "select * from actions where state = 2")
        return vo(1, [_action_to_dict(r) for r in rows])


@router.post("/queryRecord")
def query_records(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(status)

        rows = fetch_all(conn, "select * from record_view where account_id = :uid order by ID DESC", {"uid": user["id"]})
        # record_view contains account_id but Java RecordView doesn't; keep compatibility by dropping it if present
        for r in rows:
            r.pop("account_id", None)
        return vo(1, rows)


@router.post("/queryWechatGroup")
def query_wechat_group(token: str = Depends(bearer_token), record_id: int = Query(...)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2)

        record = fetch_one(conn, "select * from records where ID=:id", {"id": record_id})
        if not record:
            return vo(-1)

        if int(record.get("user_id") or 0) != int(user["id"]):
            return vo(0)

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": record["action_id"]})
        values = {
            "wechat_id": user.get("wechat_id"),
            "wechat_url": action.get("wechat_url") if action else None,
        }
        return vo(1, values)


@router.post("/attendAction")
def attend_action(token: str = Depends(bearer_token), action_id: int = Query(...), borrow: bool = Query(False)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        if int(user.get("state") or 0) != 2:
            return vo(-1, "Identify Incorrect")

        action = lock_action(conn, action_id)
        if not action or int(action.get("state") or 0) != 2:
            return vo(0, "No action")

        in_action = fetch_all(
            conn,
            "select ID from records where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
            for_update=True,
        )
        in_waiting = fetch_all(
            conn,
            "select ID from waiting where user_id=:uid and action_id=:aid",
            {"uid": user["id"], "aid": action_id},
            for_update=True,
        )
        if in_action or in_waiting:
            return vo(1, "Repeated")

        now_count = len(fetch_all(
            conn, "select ID from records where action_id=:aid", {"aid": action_id}, for_update=True,
        ))
        if now_count >= int(action.get("max_num") or 0):
            return vo(2, "Full")

        sign_code = str(uuid.uuid4())
        exec_one(
            conn,
            "insert into records(user_id, action_id, sign_code, borrow, state) values (:uid, :aid, :code, :borrow, :state)",
            {"uid": user["id"], "aid": action_id, "code": sign_code, "borrow": int(borrow), "state": 0},
        )
        if borrow:
            exec_one(conn, "update actions set borrow_num = borrow_num + 1 where ID=:id", {"id": action_id})

        return vo(3, "Success")


@router.post("/cancelAction")
def cancel_action(token: str = Depends(bearer_token), record_id: int = Query(...)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        record_ref = fetch_one(conn, "select action_id from records where ID=:id", {"id": record_id})
        if not record_ref:
            return vo(-1, "No Record")

        action = lock_action(conn, record_ref["action_id"])
        record = fetch_one(conn, "select * from records where ID=:id", {"id": record_id}, for_update=True)
        if not record:
            return vo(-1, "No Record")
        if action and int(action.get("state") or 0) > 2:
            return vo(0, "Can not Cancel!")

        if int(record.get("user_id") or 0) != int(user["id"]):
            return vo(1, "User Not Match")

        waiting_rows = fetch_all(
            conn, "select * from waiting where action_id=:aid order by `rank`", {"aid": record["action_id"]},
            for_update=True,
        )
        if waiting_rows:
            wait = waiting_rows[0]
            new_code = str(uuid.uuid4())
            exec_one(
                conn,
                "update records set sign_code=:code, user_id=:uid, borrow=:borrow where ID=:rid",
                {"code": new_code, "uid": wait["user_id"], "borrow": int(wait["borrow"]), "rid": record_id},
            )
            exec_one(
                conn,
                "update waiting set `rank` = `rank`-1 where action_id=:aid and `rank`>=:con_rank",
                {"aid": record["action_id"], "con_rank": 1},
            )
            exec_one(conn, "delete from waiting where ID=:id", {"id": wait["id"]})

            if int(record.get("borrow") or 0) == 1 and int(wait.get("borrow") or 0) == 0:
                exec_one(conn, "update actions set borrow_num = borrow_num - 1 where ID=:id", {"id": record["action_id"]})
            if int(wait.get("borrow") or 0) == 1 and int(record.get("borrow") or 0) == 0:
                exec_one(conn, "update actions set borrow_num = borrow_num + 1 where ID=:id", {"id": record["action_id"]})
        else:
            exec_one(conn, "delete from records where ID=:rid", {"rid": record_id})
            if int(record.get("borrow") or 0) == 1:
                exec_one(conn, "update actions set borrow_num = borrow_num - 1 where ID=:id", {"id": record["action_id"]})

        return vo(2, "Successful")
