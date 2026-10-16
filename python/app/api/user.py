from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, Query, Request

from .auth_transport import bearer_token

from ..db import exec_one, fetch_all, fetch_one, sql_binary, tx
from ..passwords import hash_password, verify_user_password
from ..rate_limit import clear_login_account_attempts, reserve_login_request
from ..response import vo
from ..utils import PASSWORD_PATTERN, encrypt_md5, mask_equip_id, new_token
from .common import token_verify_member

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/login")
def login(request: Request, username: str = Body("", embed=True), password: str = Body("", embed=True)):
    if not reserve_login_request(request, username):
        return vo(-3, "Too many login attempts")
    with tx() as conn:
        user = fetch_one(conn, f"select * from users where {sql_binary('username')}=:username", {"username": username})
        if not user:
            return vo(-2)
        if not verify_user_password(conn, user, password):
            return vo(-2)

        clear_login_account_attempts(conn, username)

        state = int(user.get("state") or 0)
        token_value: str | None = None
        if 0 < state < 4:
            token_value = new_token()
            out_time = datetime.now() + timedelta(hours=3)
            exec_one(conn, "delete from tokens where user_id=:uid", {"uid": user["id"]})
            exec_one(
                conn,
                "insert into tokens(user_id, token, out_time) values (:uid, :token, :out_time)",
                {"uid": user["id"], "token": token_value, "out_time": out_time},
            )
        return vo(state, token_value)


@router.post("/loginByEquip", deprecated=True)
def login_by_equip():
    # A browser fingerprint is reproducible and cannot authenticate a person.
    # Keep the old route explicit for clients, but never issue a token here.
    return vo(-2, "Device-only login is disabled. Use your password.")


@router.post("/verify")
def verify(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, user_view = token_verify_member(conn, token)
        return vo(status, user_view)


@router.post("/password")
def change_password(
    token: str = Depends(bearer_token),
    origin_pass: str = Body("", embed=True),
    new_pass: str = Body("", embed=True),
):
    if not PASSWORD_PATTERN.match(new_pass):
        return vo(-2, "Password Invalid!")

    with tx() as conn:
        status, user_view = token_verify_member(conn, token)
        if status <= 0 or not user_view:
            return vo(status, "Token or Account Error.")

        correct = fetch_one(conn, "select id, password, state from users where ID=:uid", {"uid": user_view["id"]})
        if not correct or not verify_user_password(conn, correct, origin_pass):
            return vo(1, "Origen Password Error.")

        rc = exec_one(conn, "update users set password=:pwd where ID=:uid", {"pwd": hash_password(new_pass), "uid": user_view["id"]})
        if rc > 0:
            return vo(3, "Successful!")
        return vo(2, "Database Error!")


@router.post("/queryEquips")
def query_equips(token: str = Depends(bearer_token), local: str = Body("", embed=True)):
    with tx() as conn:
        status, user_view = token_verify_member(conn, token)
        if status <= 0 or not user_view:
            return vo(status)

        local_md5 = encrypt_md5(local)
        equips = fetch_all(conn, "select * from equipment where user_id=:uid", {"uid": user_view["id"]})

        no_add = False
        for equip in equips:
            if equip.get("equip_id") == local_md5:
                no_add = True
            equip["equip_id"] = mask_equip_id(equip.get("equip_id"))

        if len(equips) >= 5:
            no_add = True

        return vo(2 if no_add else 1, equips)


@router.post("/newEquipment", deprecated=True)
def new_equipment():
    # No new fingerprint credentials while device-only login is disabled.
    return vo(-2, "Device-only login is disabled. Use your password.")


@router.post("/deleteEquipment")
def delete_equipment(token: str = Depends(bearer_token), id: int = Query(...)):
    with tx() as conn:
        status, user_view = token_verify_member(conn, token)
        if status <= 0 or not user_view:
            return vo(-2, "Login Error")

        equip = fetch_one(conn, "select * from equipment where id=:id", {"id": id})
        if not equip:
            return vo(-1, "Not Record")

        if int(equip.get("user_id") or 0) != int(user_view["id"]):
            return vo(0, "Not Belong")

        exec_one(conn, "delete from equipment where id=:id", {"id": id})
        return vo(1, "Successful!")


@router.post("/contact")
def contact(
    token: str = Depends(bearer_token),
    origin_pass: str = Body("", embed=True),
    email: str = Body("", embed=True),
    phone: str = Body("", embed=True),
    wechat_id: str = Body("", embed=True),
):
    with tx() as conn:
        status, user_view = token_verify_member(conn, token)
        if status <= 0 or not user_view:
            return vo(status, "Token or Account Error.")

        correct = fetch_one(conn, "select id, password, state from users where ID=:uid", {"uid": user_view["id"]})
        if not correct or not verify_user_password(conn, correct, origin_pass):
            return vo(1, "Origen Password Error.")

        rc = exec_one(
            conn,
            "update users set phone=:phone, email=:email, wechat_id=:wechat_id where ID=:uid",
            {"phone": phone, "email": email, "wechat_id": wechat_id, "uid": user_view["id"]},
        )
        if rc > 0:
            return vo(3, "Successful!")
        return vo(2, "Database Error!")


@router.post("/logout")
def logout(token: str = Depends(bearer_token)):
    # Java returns int
    with tx() as conn:
        exists = fetch_one(conn, "select count(*) as c from tokens where tokens.token=:token", {"token": token})
        if not exists or int(exists["c"]) == 0:
            return -1
        exec_one(conn, "delete from tokens where token=:token", {"token": token})
        return 0


@router.post("/register")
def register(
    username: str = Body("", embed=True),
    password: str = Body("", embed=True),
    name: str = Body("", embed=True),
    card_id: str = Body("", embed=True),
    phone: str = Body("", embed=True),
    wechat_id: str = Body("", embed=True),
    student_id: str = Body("", embed=True),
    email: str = Body("", embed=True),
):
    if not PASSWORD_PATTERN.match(password):
        return vo(-1, "Invalid Password Format")

    with tx() as conn:
        exists = fetch_one(conn, "select * from users where username=:username", {"username": username})
        if exists:
            return vo(-1, "The currently registered username already exists, please change it and try again\n")

        password_hash = hash_password(password)
        exec_one(
            conn,
            "insert into users(username, password, name, card_id, phone, state, wechat_id, student_id, email)"
            " values (:username, :password, :name, :card_id, :phone, :state, :wechat_id, :student_id, :email)",
            {
                "username": username,
                "password": password_hash,
                "name": name,
                "card_id": card_id,
                "phone": phone,
                "state": -1,
                "wechat_id": wechat_id,
                "student_id": student_id,
                "email": email,
            },
        )
        return vo(0, "Your account has been registered. Please wait for the review to be passed before use.")
