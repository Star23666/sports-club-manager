from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Body, Depends, Query

from .auth_transport import bearer_token

from ..db import exec_one, fetch_all, fetch_one, lock_action, tx
from ..response import vo
from ..utils import parse_maybe_datetime
from .common import token_verify_member

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.post("/queryAction")
def query_action(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2)
        if int(user.get("state") or 0) != 3:
            return vo(-1)

        rows = fetch_all(conn, "select * from staff_action_view where staff_id=:sid order by ID DESC", {"sid": user["id"]})
        return vo(1, rows)


@router.post("/queryActionMember")
def query_action_member(token: str = Depends(bearer_token), action_id: int = Query(...)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2)
        if int(user.get("state") or 0) != 3:
            return vo(-1)

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action or int(action.get("staff_user_id") or 0) != int(user["id"]):
            return vo(2, "Staff Not Match")

        rows = fetch_all(conn, "select * from staff_member_view where action_id=:aid", {"aid": action_id})
        return vo(1, rows)


@router.post("/startSign")
def start_sign(token: str = Depends(bearer_token), action_id: int = Query(...)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Error")
        if int(user.get("state") or 0) != 3:
            return vo(-1, "No Staff")

        action = lock_action(conn, action_id)
        if not action:
            return vo(0, "No Action")
        if int(action.get("state") or 0) != 3:
            return vo(1, "Action State Error")
        if int(action.get("staff_user_id") or 0) != int(user["id"]):
            return vo(2, f"Staff No Match:{user['id']}/{action.get('staff_user_id')}")

        now = datetime.now()
        open_time = parse_maybe_datetime(action.get("open_time"))
        if action.get("open_time") and (open_time is None or open_time > now):
            return vo(3, "Time Exceed")

        exec_one(conn, "delete from transfer where exists(select * from records where ID = record_id and action_id = :aid)", {"aid": action_id})
        exec_one(conn, "update actions set state = :state where ID = :aid", {"state": 4, "aid": action_id})
        return vo(4, "Successful!")


@router.post("/stopAction")
def stop_action(token: str = Depends(bearer_token), action_id: int = Query(...)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Error")
        if int(user.get("state") or 0) < 3:
            return vo(-1, "No Staff")

        action = lock_action(conn, action_id)
        if not action:
            return vo(0, "No Action")
        if int(action.get("state") or 0) != 4:
            return vo(1, "Action State Error")
        if int(action.get("staff_user_id") or 0) != int(user["id"]):
            return vo(2, f"Staff No Match:{user['id']}/{action.get('staff_user_id')}")

        now = datetime.now()
        close_time = parse_maybe_datetime(action.get("close_time"))
        if action.get("close_time") and (close_time is None or close_time > now):
            return vo(3, "Time Exceed")

        exec_one(
            conn,
            "update users set unsigned_num = unsigned_num + 1 where exists(select * from records where user_id = users.id and action_id = :aid and state = 0)",
            {"aid": action_id},
        )
        exec_one(conn, "update actions set state = :state where ID = :aid", {"state": 5, "aid": action_id})
        exec_one(
            conn,
            "update users set unsigned_num = (select count(*) from actions where staff_user_id = :uid and state = 5) where ID = :uid",
            {"uid": user["id"]},
        )
        newly_restricted = fetch_all(
            conn,
            "select ID from users where state = 2 and unsigned_num >= 3 and "
            "exists(select 1 from records where records.user_id = users.ID and action_id = :aid and records.state = 0)",
            {"aid": action_id},
            for_update=True,
        )
        exec_one(
            conn,
            "update users set state = 1 where state = 2 and unsigned_num >= 3 and exists(select * from records where users.ID = user_id and action_id = :aid and state = 0)",
            {"aid": action_id},
        )
        for affected in newly_restricted:
            exec_one(conn, "delete from tokens where user_id=:uid", {"uid": affected["id"]})
        return vo(4, "Successful!")


@router.post("/querySign")
def query_sign(token: str = Depends(bearer_token), sign_code: str = Body("", embed=True)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2)
        if int(user.get("state") or 0) != 3:
            return vo(-1)

        record = fetch_one(conn, "select * from records where sign_code=:code", {"code": sign_code})
        if not record:
            return vo(0)

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": record["action_id"]})
        if not action or int(action.get("staff_user_id") or 0) != int(user["id"]):
            return vo(2, "Staff Not Match")
        mem = fetch_one(conn, "select * from user_view where ID=:id", {"id": record["user_id"]})

        values = {
            "mem_inf": mem,
            "act_inf": action,
            "borrow": record.get("borrow"),
            "signed": record.get("state"),
        }

        if int(record.get("state") or 0) == 1:
            st = 1
        elif int(action.get("state") or 0) < 4:
            st = 3
        elif int(action.get("state") or 0) == 5:
            st = 4
        else:
            st = 5

        return vo(st, values)


@router.post("/finishSign")
def finish_sign(token: str = Depends(bearer_token), sign_code: str = Body("", embed=True)):
    with tx(immediate=True) as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Sign Error")
        if int(user.get("state") or 0) != 3:
            return vo(-1, "Identify No Match")

        record_ref = fetch_one(conn, "select action_id from records where sign_code=:code", {"code": sign_code})
        if not record_ref:
            return vo(0, "No Record")

        action = lock_action(conn, record_ref["action_id"])
        record = fetch_one(conn, "select * from records where sign_code=:code", {"code": sign_code}, for_update=True)
        if not record:
            return vo(0, "No Record")
        if not action or int(action.get("staff_user_id") or 0) != int(user["id"]):
            return vo(2, "Staff Not Match")
        if int(record.get("state") or 0) == 1:
            return vo(1, "Finished Sign")
        if int(action.get("state") or 0) < 4:
            return vo(3, "Action no Begin")
        if int(action.get("state") or 0) == 5:
            return vo(4, "Finished Action")

        exec_one(conn, "update records set state=:state where id=:rid", {"state": 1, "rid": record["id"]})
        exec_one(conn, "update records set sign_time=:t where id=:rid", {"t": datetime.now(), "rid": record["id"]})
        return vo(5, "Successful")
