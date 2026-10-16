from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Query

from .auth_transport import bearer_token

from ..db import exec_one, fetch_all, fetch_one, tx
from ..response import vo
from ..passwords import hash_password
from ..utils import PASSWORD_PATTERN
from .common import token_verify_admin

router = APIRouter(prefix="/admin/api/member", tags=["admin-member"])


def _user_to_view(row: dict) -> dict:
    # Match Java UserView fields
    keys = {"id", "username", "name", "phone", "state", "wechat_id", "email", "student_id", "card_id", "unsigned_num"}
    return {k: row.get(k) for k in keys}


@router.post("/queryMembers")
def query_members(
    token: str = Depends(bearer_token),
    name: str = Query(""),
    student_id: str = Query(""),
    state: int = Query(-1),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _ = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        offset = (page_number - 1) * page_size
        name_pattern = f"%{name}%"
        sid_pattern = f"%{student_id}%"
        if state == -1:
            count = fetch_one(
                conn,
                "select count(*) as c from users where name like :name_pattern and student_id like :sid_pattern and state >= 0",
                {"name_pattern": name_pattern, "sid_pattern": sid_pattern},
            )
            rows = fetch_all(
                conn,
                "select * from users where name like :name_pattern and student_id like :sid_pattern and state >= 0 limit :ps offset :off",
                {"name_pattern": name_pattern, "sid_pattern": sid_pattern, "ps": page_size, "off": offset},
            )
        else:
            count = fetch_one(
                conn,
                "select count(*) as c from users where name like :name_pattern and student_id like :sid_pattern and state = :state",
                {"name_pattern": name_pattern, "sid_pattern": sid_pattern, "state": state},
            )
            rows = fetch_all(
                conn,
                "select * from users where name like :name_pattern and student_id like :sid_pattern and state = :state limit :ps offset :off",
                {"name_pattern": name_pattern, "sid_pattern": sid_pattern, "state": state, "ps": page_size, "off": offset},
            )

        return vo(int(count["c"]) if count else 0, [_user_to_view(r) for r in rows])


@router.post("/queryReviewMembers")
def query_review_members(
    token: str = Depends(bearer_token),
    name: str = Query(""),
    student_id: str = Query(""),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _ = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        offset = (page_number - 1) * page_size
        name_pattern = f"%{name}%"
        sid_pattern = f"%{student_id}%"
        count = fetch_one(
            conn,
            "select count(*) as c from users where name like :name_pattern and student_id like :sid_pattern and state = -1",
            {"name_pattern": name_pattern, "sid_pattern": sid_pattern},
        )
        rows = fetch_all(
            conn,
            "select * from users where name like :name_pattern and student_id like :sid_pattern and state = -1 limit :ps offset :off",
            {"name_pattern": name_pattern, "sid_pattern": sid_pattern, "ps": page_size, "off": offset},
        )
        return vo(int(count["c"]) if count else 0, [_user_to_view(r) for r in rows])


@router.post("/queryUnsignedMembers")
def query_unsigned_members(
    token: str = Depends(bearer_token),
    name: str = Query(""),
    student_id: str = Query(""),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _ = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        offset = (page_number - 1) * page_size
        name_pattern = f"%{name}%"
        sid_pattern = f"%{student_id}%"
        count = fetch_one(
            conn,
            "select count(*) as c from users where state >= 0 and state < 3 and name like :name_pattern and student_id like :sid_pattern",
            {"name_pattern": name_pattern, "sid_pattern": sid_pattern},
        )
        rows = fetch_all(
            conn,
            "select * from users where state >= 0 and state < 3 and name like :name_pattern and student_id like :sid_pattern "
            "order by unsigned_num DESC, id ASC limit :ps offset :off",
            {"name_pattern": name_pattern, "sid_pattern": sid_pattern, "ps": page_size, "off": offset},
        )
        return vo(int(count["c"]) if count else 0, [_user_to_view(r) for r in rows])


@router.post("/updateUserInf")
def update_user_inf(
    token: str = Depends(bearer_token),
    id: int = Query(...),
    username: str = Query(""),
    state: int = Query(...),
    name: str = Query(""),
    student_id: str = Query(""),
    card_id: str = Query(""),
    phone: str = Query(""),
    wechat_id: str = Query(""),
    email: str = Query(""),
):
    with tx() as conn:
        ok, admin = token_verify_admin(conn, token)
        if ok <= 0 or not admin:
            return vo(-2, "Login Error")

        if int(admin["id"]) == int(id) and int(state) != int(admin.get("state") or 0):
            return vo(-1, "Banned Update Myself")

        existing = fetch_one(conn, "select * from users where username=:u", {"u": username})
        if existing and int(existing.get("id") or 0) != int(id):
            return vo(0, "Username Repeated")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": id})
        if not user:
            return vo(1, "User Not Exist")

        # state transitions logic
        if int(user.get("state") or 0) == 3 and int(state) != 3:
            in_charge = fetch_one(conn, "select count(*) as c from actions where staff_user_id=:uid and state != 5", {"uid": id})
            if in_charge and int(in_charge["c"]) > 0:
                return vo(2, "User Actions Exists")
            exec_one(conn, "update users set unsigned_num=:num where id=:uid", {"num": 0, "uid": id})

        if int(user.get("state") or 0) != 3 and int(state) == 3:
            exec_one(conn, "delete from records where user_id=:uid", {"uid": id})
            exec_one(conn, "delete from waiting where user_id=:uid", {"uid": id})
            finished = fetch_one(conn, "select count(*) as c from actions where staff_user_id=:uid and state = 5", {"uid": id})
            exec_one(conn, "update users set unsigned_num=:num where id=:uid", {"num": int(finished["c"]) if finished else 0, "uid": id})

        exec_one(
            conn,
            "update users set username=:username, name=:name, card_id=:card_id, phone=:phone, state=:state, wechat_id=:wechat_id, email=:email, student_id=:student_id where ID=:id",
            {
                "id": id,
                "username": username,
                "state": state,
                "name": name,
                "card_id": card_id,
                "phone": phone,
                "wechat_id": wechat_id,
                "email": email,
                    "student_id": student_id,
            },
        )
        return vo(3, "Successfully")


@router.post("/updateUserPassword")
def update_user_password(token: str = Depends(bearer_token), user_id: int = Query(...), password: str = Body("", embed=True)):
    if not PASSWORD_PATTERN.match(password):
        return vo(-2, "Password Invalid!")

    with tx() as conn:
        ok, admin = token_verify_admin(conn, token)
        if ok <= 0 or not admin:
            return vo(-2, "Login Error")

        if int(admin["id"]) == int(user_id):
            return vo(-1, "Banned Update Myself")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": user_id})
        if not user:
            return vo(0, "User Not Exist")

        exec_one(conn, "update users set password=:pwd where ID=:id", {"pwd": hash_password(password), "id": user_id})
        return vo(1, "Successfully")


@router.post("/deleteUser")
def delete_user(token: str = Depends(bearer_token), user_id: int = Query(...)):
    with tx() as conn:
        ok, admin = token_verify_admin(conn, token)
        if ok <= 0 or not admin:
            return vo(-2, "Login Error")

        if int(admin["id"]) == int(user_id):
            return vo(-1, "Banned Update Myself")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": user_id})
        if not user:
            return vo(0, "User Not Exist")

        if int(user.get("state") or 0) == 3:
            in_charge = fetch_one(conn, "select count(*) as c from actions where staff_user_id=:uid and state != 5", {"uid": user_id})
            if in_charge and int(in_charge["c"]) > 0:
                return vo(1, "User Actions Exists")

        exec_one(conn, "delete from users where ID=:id", {"id": user_id})
        return vo(2, "Successfully")


@router.post("/passUser")
def pass_user(token: str = Depends(bearer_token), user_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": user_id})
        if not user or int(user.get("state") or 0) > 0:
            return vo(0, "User Not Exist")

        exec_one(conn, "update users set state = 2 where ID=:id", {"id": user_id})
        return vo(1, "Successfully")


@router.post("/clearUserUnsigned")
def clear_user_unsigned(token: str = Depends(bearer_token), user_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": user_id})
        if not user:
            return vo(0, "User Not Exist")

        if int(user.get("state") or 0) not in (0, 1, 2):
            return vo(1, "User Kind Not Match")

        u = exec_one(conn, "update users set unsigned_num=:num where id=:uid", {"num": 0, "uid": user_id})
        exec_one(conn, "update users set state = 2 where ID=:id", {"id": user_id})
        return vo(2, f"Successfully:{bool(u)}")


@router.post("/resetUserUnsigned")
def reset_user_unsigned(token: str = Depends(bearer_token), user_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        user = fetch_one(conn, "select * from users where ID=:id", {"id": user_id})
        if not user:
            return vo(0, "User Not Exist")

        if int(user.get("state") or 0) not in (0, 1, 2):
            return vo(1, "User Kind Not Match")

        num = fetch_one(
            conn,
            "select count(*) as c from records, actions where records.user_id = :uid and records.state = 0 and records.action_id = actions.ID and actions.state = 5",
            {"uid": user_id},
        )
        u = exec_one(conn, "update users set unsigned_num=:num where id=:uid", {"num": int(num["c"]) if num else 0, "uid": user_id})
        exec_one(conn, "update users set state = 1 where ID = :uid and unsigned_num >= 3", {"uid": user_id})
        return vo(2, f"Successfully1:{bool(u)}")


@router.post("/queryStaffMembers")
def query_staff_members(token: str = Depends(bearer_token), name: str = Query(""), select_id: int = Query(-1)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        rows = fetch_all(
            conn,
            "select * from users where name like :name_pattern and state = 3 and id != :select_id order by unsigned_num ASC limit 5",
            {"name_pattern": f"%{name}%", "select_id": select_id},
        )
        out = [_user_to_view(r) for r in rows]
        if select_id != -1:
            sel = fetch_one(conn, "select * from user_view where ID=:id", {"id": select_id})
            if sel:
                out.insert(0, sel)
        return vo(1, out)


@router.post("/queryInboxData")
def query_inbox_data(token: str = Depends(bearer_token)):
    with tx() as conn:
        ok, admin = token_verify_admin(conn, token)
        if ok <= 0 or not admin:
            return vo(-1)

        total_actions = fetch_one(conn, "select count(*) as c from actions where title like :t_pattern", {"t_pattern": "%%"})
        total_members = fetch_one(conn, "select count(*) as c from users where state < 3 and state >= 0")
        total_stuffs = fetch_one(conn, "select count(*) as c from users where name like :n_pattern and student_id like :s_pattern and state = 3", {"n_pattern": "%%", "s_pattern": "%%"})
        total_records = fetch_one(conn, "select count(*) as c from records")
        total_unsigned = fetch_one(
            conn,
            "select count(*) as c from records, actions where records.state = 0 and records.action_id = actions.id and actions.state = 5",
        )
        finished_actions = fetch_one(conn, "select count(*) as c from actions where title like :t_pattern and state=5", {"t_pattern": "%%"})

        unsign_list = fetch_all(conn, "select * from users where state >= 0 and state < 3 order by unsigned_num DESC, id ASC limit 5")
        stuff_list = fetch_all(conn, "select * from users where state = 3 order by unsigned_num DESC, id ASC limit 5")

        inbox = {
            "user_inf": admin,
            "totalActions": int(total_actions["c"]) if total_actions else 0,
            "totalMembers": int(total_members["c"]) if total_members else 0,
            "totalStuffs": int(total_stuffs["c"]) if total_stuffs else 0,
            "totalRecords": int(total_records["c"]) if total_records else 0,
            "totalUnsignedRecords": int(total_unsigned["c"]) if total_unsigned else 0,
            "avarageWorkTimes": (
                (float(finished_actions["c"]) / float(total_stuffs["c"])) if total_stuffs and int(total_stuffs["c"]) > 0 else 0.0
            ),
            "UnsignMemberList": [_user_to_view(r) for r in unsign_list],
            "StuffMemberList": [_user_to_view(r) for r in stuff_list],
        }

        return vo(1, inbox)
