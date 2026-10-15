from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Query

from ..db import exec_one, fetch_one, tx
from ..email_service import send_reset_email
from ..response import vo
from ..settings import settings
from ..passwords import hash_password
from ..utils import EMAIL_PATTERN, PASSWORD_PATTERN

router = APIRouter(prefix="/api/find", tags=["find"])


@router.post("/queryUserName")
def query_username(name: str = Query(""), student_id: str = Query("")):
    with tx() as conn:
        if not name.strip() or not student_id.strip():
            return vo(-1, "Not Found")

        user = fetch_one(conn, "select * from user_view where name=:name and student_id=:sid", {"name": name, "sid": student_id})
        if not user:
            return vo(-1, "Not Found")

        return vo(0, user.get("username"))


@router.post("/sendResetEmail")
def send_reset_email_api(
    name: str = Query(""),
    student_id: str = Query(""),
    username: str = Query(""),
    StudentEmail: int | None = Query(None),
):
    with tx() as conn:
        user = fetch_one(conn, "select * from users where username=:u", {"u": username})
        if not user:
            return vo(-2, "Not Found")

        if user.get("name") != name or user.get("student_id") != student_id:
            return vo(-2, "Not Found")

        code_row = fetch_one(conn, "select * from verifycode where user_id=:uid", {"uid": user["id"]})
        if code_row:
            judge_time = datetime.now() + timedelta(minutes=28)
            if code_row.get("out_time") and judge_time < code_row["out_time"]:
                return vo(-1, "Time Limit")
            exec_one(conn, "delete from verifycode where user_id=:uid", {"uid": user["id"]})

        if StudentEmail is None:
            email = (user.get("email") or "").strip()
            if not email or not EMAIL_PATTERN.match(email):
                return vo(0, "Email Error")
        else:
            domain = settings.email_domain or "example.com"
            email = f"{user.get('student_id')}@{domain}"

        code = str(uuid.uuid4())
        out_time = datetime.now() + timedelta(minutes=30)
        exec_one(
            conn,
            "insert into verifycode(user_id, code, out_time) values (:uid, :code, :out_time)",
            {"uid": user["id"], "code": code, "out_time": out_time},
        )

        try:
            ok = send_reset_email(email, user.get("name") or "", code)
        except Exception:
            ok = False

        # Java 侧发送失败会抛异常（500）；这里返回更友好一点，但保持 status=1 的成功语义需 SMTP 配置。
        if not ok:
            return vo(0, "Email Error")

        return vo(1, "Successfully!")


@router.post("/resetPassword")
def reset_password(code: str = Body("", embed=True), password: str = Body("", embed=True)):
    if not PASSWORD_PATTERN.match(password):
        return vo(-2, "Password Invalid!")
    if not code.strip():
        return vo(-2, "Not Found")

    with tx() as conn:
        vc = fetch_one(conn, "select * from verifycode where code=:code", {"code": code})
        if not vc:
            return vo(-2, "Not Found")

        exec_one(conn, "delete from verifycode where user_id=:uid", {"uid": vc["user_id"]})
        user = fetch_one(conn, "select * from users where ID=:uid", {"uid": vc["user_id"]})
        if not user:
            return vo(-2, "Not Found")

        if vc.get("out_time") and datetime.now() > vc["out_time"]:
            return vo(-1, "Time Exceed")

        exec_one(conn, "update users set password=:pwd where ID=:uid", {"pwd": hash_password(password), "uid": user["id"]})
        return vo(0, "Successfully!")
