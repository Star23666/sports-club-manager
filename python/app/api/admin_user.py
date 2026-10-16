from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Query

from .auth_transport import bearer_token

from ..db import exec_one, fetch_one, tx
from ..response import vo
from ..passwords import hash_password, verify_user_password
from ..utils import PASSWORD_PATTERN
from .common import login_common, token_verify_admin

router = APIRouter(prefix="/admin/api/user", tags=["admin-user"])


@router.post("/login")
def admin_login(username: str = Query(""), password: str = Body("", embed=True)):
    with tx() as conn:
        status, token_value = login_common(conn, username, password, admin=True)
        return vo(status, token_value if status == 0 else None)


@router.post("/verify")
def verify(token: str = Depends(bearer_token)):
    with tx() as conn:
        status, user_view = token_verify_admin(conn, token)
        return vo(status, user_view)


@router.post("/password")
def change_password(token: str = Depends(bearer_token), origin_pass: str = Body("", embed=True), new_pass: str = Body("", embed=True)):
    if not PASSWORD_PATTERN.match(new_pass):
        return vo(-2, "Password Invalid!")

    with tx() as conn:
        status, user_view = token_verify_admin(conn, token)
        if status <= 0 or not user_view:
            return vo(status, "Token or Account Error.")

        correct = fetch_one(conn, "select id, password, state from users where ID=:uid", {"uid": user_view["id"]})
        if not correct or not verify_user_password(conn, correct, origin_pass):
            return vo(1, "Origen Password Error.")

        rc = exec_one(conn, "update users set password=:pwd where ID=:uid", {"pwd": hash_password(new_pass), "uid": user_view["id"]})
        if rc > 0:
            return vo(3, "Successful!")
        return vo(2, "Database Error!")


@router.post("/contact")
def contact(
    token: str = Depends(bearer_token),
    origin_pass: str = Body("", embed=True),
    email: str = Query(""),
    phone: str = Query(""),
    wechat_id: str = Query(""),
):
    with tx() as conn:
        status, user_view = token_verify_admin(conn, token)
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
