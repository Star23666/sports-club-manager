from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..db import exec_one, fetch_all, fetch_one, tx
from ..response import vo
from .common import token_verify_member

router = APIRouter(prefix="/api/transfer", tags=["transfer"])


@router.post("/queryTransfer")
def query_transfer(token: str = Query("")):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(status)

        transfers = fetch_all(
            conn,
            "select * from transfer_view where receive_user_id = :uid and receive_user_id <> send_user_id",
            {"uid": user["id"]},
        )
        if int(user.get("state") or 0) == 2:
            public_list = fetch_all(conn, "select * from transfer_view where receive_user_id = send_user_id")
            for t in public_list:
                t["receive_user"] = ""
            transfers.extend(public_list)

        return vo(1, transfers)


@router.post("/transferRecord")
def transfer_record(token: str = Query(""), record_id: int = Query(...), receive_user: str = Query("")):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        record = fetch_one(conn, "select * from records where ID=:id", {"id": record_id})
        if not record:
            return vo(-1, "No Record")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": record["action_id"]})
        if not action or int(action.get("state") or 0) != 3:
            return vo(0, "Can not Translate!")

        if int(record.get("user_id") or 0) != int(user["id"]):
            return vo(1, "User Not Match")

        cnt = fetch_one(conn, "select count(*) as c from transfer where record_id=:rid", {"rid": record_id})
        if cnt and int(cnt["c"]) > 0:
            return vo(2, "Transfer Repeted!")

        if not receive_user:
            receive_id = int(user["id"])
        else:
            ru = fetch_one(conn, "select * from users where username=:u", {"u": receive_user})
            if not ru:
                return vo(3, "No user")
            if int(ru.get("state") or 0) not in (1, 2):
                return vo(3, "No user")
            receive_id = int(ru["id"])

        exec_one(
            conn,
            "insert into transfer(record_id, send_user_id, receive_user_id) values (:rid, :sid, :rid2)",
            {"rid": record_id, "sid": user["id"], "rid2": receive_id},
        )
        return vo(4, "Successful!")


@router.post("/acceptTransfer")
def accept_transfer(token: str = Query(""), transfer_id: int = Query(...)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        transfer = fetch_one(conn, "select * from transfer where ID=:id", {"id": transfer_id})
        if not transfer:
            return vo(-1, "No Record")

        if int(transfer.get("receive_user_id") or 0) == int(transfer.get("send_user_id") or 0) and int(user.get("state") or 0) != 2:
            return vo(0, "Not Match")

        if int(transfer.get("receive_user_id") or 0) != int(user["id"]) and int(transfer.get("receive_user_id") or 0) != int(transfer.get("send_user_id") or 0):
            return vo(0, "Not Match")

        record = fetch_one(conn, "select * from records where ID=:id", {"id": transfer["record_id"]})
        if not record:
            return vo(-1, "No Record")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": record["action_id"]})
        if action:
            in_action = fetch_one(
                conn,
                "select count(*) as c from records where user_id=:uid and action_id=:aid",
                {"uid": user["id"], "aid": action["id"]},
            )
            if in_action and int(in_action["c"]) > 0 and int(record.get("user_id") or 0) != int(user["id"]):
                return vo(1, "Repeated!")

        exec_one(
            conn,
            "update records set sign_code=:code, user_id=:uid, borrow=:borrow where ID=:rid",
            {"code": str(uuid.uuid4()), "uid": user["id"], "borrow": int(record.get("borrow") or 0), "rid": record["id"]},
        )
        exec_one(conn, "delete from transfer where ID=:id", {"id": transfer_id})
        return vo(2, "Successful!")


@router.post("/refuseTransfer")
def refuse_transfer(token: str = Query(""), transfer_id: int = Query(...)):
    with tx() as conn:
        status, user = token_verify_member(conn, token)
        if status <= 0 or not user:
            return vo(-2, "Login Incorrect")

        transfer = fetch_one(conn, "select * from transfer where ID=:id", {"id": transfer_id})
        if not transfer:
            return vo(-1, "No Record")

        if int(transfer.get("receive_user_id") or 0) == int(transfer.get("send_user_id") or 0):
            return vo(0, "Not Match")

        if int(transfer.get("receive_user_id") or 0) != int(user["id"]):
            return vo(0, "Not Match")

        exec_one(conn, "delete from transfer where ID=:id", {"id": transfer_id})
        return vo(1, "Successful!")
