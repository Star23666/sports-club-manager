from __future__ import annotations

from fastapi import APIRouter, Query

from ..db import exec_one, fetch_all, fetch_one, tx
from ..response import vo
from ..utils import parse_maybe_datetime
from .common import token_verify_admin

router = APIRouter(prefix="/admin/api/action", tags=["admin-action"])


def _action_to_dict(row: dict) -> dict:
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
        "borrow_num",
    }
    return {k: row.get(k) for k in keys}


@router.post("/create")
def create_action(
    token: str = Query(""),
    title: str = Query(""),
    place: str = Query(""),
    time_range: str = Query(""),
    date: str = Query(""),
    max_num: int = Query(0),
    open_time: str = Query(""),
    close_time: str = Query(""),
    staff_user_id: int = Query(0),
    wechat_url: str = Query(""),
):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        staff = fetch_one(conn, "select * from users where ID=:id", {"id": staff_user_id})
        if not staff:
            return vo(-1, "User Not Exist")
        if int(staff.get("state") or 0) != 3:
            return vo(0, "User State Not Match")

        exec_one(
            conn,
            "insert into actions(title, place, time_range, `date`, max_num, state, open_time, close_time, wechat_url, staff_user_id)"
            " values (:title, :place, :time_range, :date, :max_num, :state, :open_time, :close_time, :wechat_url, :staff_user_id)",
            {
                "title": title,
                "place": place,
                "time_range": time_range,
                "date": date,
                "max_num": max_num,
                "state": 1,
                "open_time": parse_maybe_datetime(open_time),
                "close_time": parse_maybe_datetime(close_time),
                "wechat_url": wechat_url,
                "staff_user_id": staff_user_id,
            },
        )
        return vo(1, "Successful!")


@router.post("/queryActions")
def query_actions(
    token: str = Query(""),
    name: str = Query(""),
    state: int = Query(0),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2)

        offset = (page_number - 1) * page_size
        title_pattern = f"%{name}%"
        if state == 0:
            count = fetch_one(conn, "select count(*) as c from actions where title like :t_pattern", {"t_pattern": title_pattern})
            rows = fetch_all(
                conn,
                "select * from actions where title like :t_pattern order by id DESC limit :ps offset :off",
                {"t_pattern": title_pattern, "ps": page_size, "off": offset},
            )
        else:
            count = fetch_one(conn, "select count(*) as c from actions where title like :t_pattern and state=:s", {"t_pattern": title_pattern, "s": state})
            rows = fetch_all(
                conn,
                "select * from actions where title like :t_pattern and state=:s order by id DESC limit :ps offset :off",
                {"t_pattern": title_pattern, "s": state, "ps": page_size, "off": offset},
            )

        return vo(int(count["c"]) if count else 0, [_action_to_dict(r) for r in rows])


@router.post("/deleteAction")
def delete_action(token: str = Query(""), action_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action:
            return vo(-1, "Action Not Exist")

        exec_one(conn, "delete from actions where ID=:id", {"id": action_id})
        return vo(1, "Successfully")


@router.post("/update")
def update_action(
    token: str = Query(""),
    id: int = Query(...),
    title: str = Query(""),
    place: str = Query(""),
    time_range: str = Query(""),
    date: str = Query(""),
    max_num: int = Query(0),
    open_time: str = Query(""),
    close_time: str = Query(""),
    staff_user_id: int = Query(0),
    wechat_url: str = Query(""),
):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        action1 = fetch_one(conn, "select * from actions where ID=:id", {"id": id})
        if not action1:
            return vo(-1, "Action Not Exist")

        state = int(action1.get("state") or 0)
        if state > 1:
            if (
                (action1.get("title") != title)
                or (action1.get("place") != place)
                or (action1.get("date") != date)
                or (action1.get("time_range") != time_range)
                or int(action1.get("max_num") or 0) != int(max_num)
            ):
                return vo(0, "Can't change Base Inf")

        if state > 3:
            return vo(1, "Can't change Inf")

        staff = fetch_one(conn, "select * from users where ID=:id", {"id": staff_user_id})
        if not staff:
            return vo(2, "User Not Exist")
        if int(staff.get("state") or 0) != 3:
            return vo(3, "User State Not Match")

        exec_one(
            conn,
            "update actions set title=:title, place=:place, date=:date, max_num=:max_num, state=:state, open_time=:open_time, close_time=:close_time, staff_user_id=:staff_user_id, wechat_url=:wechat_url, time_range=:time_range where ID=:id",
            {
                "id": id,
                "title": title,
                "place": place,
                "date": date,
                "max_num": max_num,
                "state": state,
                "open_time": parse_maybe_datetime(open_time),
                "close_time": parse_maybe_datetime(close_time),
                "staff_user_id": staff_user_id,
                "wechat_url": wechat_url,
                "time_range": time_range,
            },
        )
        return vo(4, "Successful!")


@router.post("/releaseAction")
def release_action(token: str = Query(""), action_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action:
            return vo(-1, "No Action")

        if int(action.get("state") or 0) == 2:
            return vo(1, "Action Has Opened")

        if int(action.get("state") or 0) not in (1, 3):
            return vo(0, "Action State Error")

        exec_one(conn, "update actions set state = :state where ID = :id", {"state": 2, "id": action_id})
        return vo(2, "Successful!")


@router.post("/stopRegisterAction")
def stop_register_action(token: str = Query(""), action_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action:
            return vo(-1, "No Action")

        if int(action.get("state") or 0) != 2:
            return vo(0, "Action State Error")

        exec_one(conn, "delete from waiting where action_id = :aid", {"aid": action_id})
        exec_one(conn, "update actions set state = :state where ID = :id", {"state": 3, "id": action_id})
        return vo(1, "Successful!")


@router.post("/stopAction")
def stop_action(token: str = Query(""), action_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": action_id})
        if not action:
            return vo(-1, "No Action")

        if int(action.get("state") or 0) != 4:
            return vo(0, "Action State Error")

        exec_one(conn, "update actions set state = :state where ID = :id", {"state": 5, "id": action_id})
        exec_one(
            conn,
            "update users set unsigned_num = unsigned_num + 1 where exists(select * from records where user_id = users.id and action_id = :aid and state = 0)",
            {"aid": action_id},
        )
        exec_one(
            conn,
            "update users set unsigned_num = (select count(*) from actions where staff_user_id = :uid and state = 5) where ID = :uid",
            {"uid": action.get("staff_user_id")},
        )
        exec_one(
            conn,
            "update users set state = 1 where state = 2 and unsigned_num >= 3 and exists(select * from records where users.ID = user_id and action_id = :aid and state = 0)",
            {"aid": action_id},
        )
        return vo(1, "Successful!")


@router.post("/reSign")
def resign(token: str = Query(""), record_id: int = Query(...), sign_code: str = Query("")):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2, "Login Error")

        record = fetch_one(conn, "select * from records where ID = :rid and sign_code = :sc", {"rid": record_id, "sc": sign_code})
        if not record:
            return vo(-1, "Not Find")

        if int(record.get("state") or 0) == 1:
            return vo(0, "Signed")

        action = fetch_one(conn, "select * from actions where ID=:id", {"id": record["action_id"]})
        if action and int(action.get("state") or 0) < 4:
            return vo(1, "Action State Error")

        exec_one(conn, "update records set state=:s where id=:rid", {"s": 1, "rid": record_id})
        if action and int(action.get("state") or 0) == 5:
            exec_one(conn, "update users set unsigned_num = unsigned_num - 1 where ID=:id and unsigned_num > 0", {"id": record["user_id"]})
            exec_one(conn, "update users set state = 2 where ID = :uid and unsigned_num < 3", {"uid": record["user_id"]})

        return vo(2, "Successful")


@router.post("/queryActionMembers")
def query_action_members(token: str = Query(""), action_id: int = Query(...)):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-2)

        rows = fetch_all(conn, "select * from staff_member_view where action_id=:aid", {"aid": action_id})
        return vo(1, rows)


@router.post("/queryRecords")
def query_records(
    token: str = Query(""),
    name: str = Query(""),
    title: str = Query(""),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        offset = (page_number - 1) * page_size
        name_pattern = f"%{name}%"
        title_pattern = f"%{title}%"
        count = fetch_one(
            conn,
            "select count(*) as c from record_view where account_name like :name_pattern and action_title like :title_pattern",
            {"name_pattern": name_pattern, "title_pattern": title_pattern},
        )
        rows = fetch_all(
            conn,
            "select * from record_view where account_name like :name_pattern and action_title like :title_pattern order by id DESC limit :ps offset :off",
            {"name_pattern": name_pattern, "title_pattern": title_pattern, "ps": page_size, "off": offset},
        )
        for r in rows:
            r["sign_code"] = "隱私字段，不予顯示"
        return vo(int(count["c"]) if count else 0, rows)


@router.post("/queryWorkRecords")
def query_work_records(
    token: str = Query(""),
    name: str = Query(""),
    title: str = Query(""),
    page_size: int = Query(10),
    page_number: int = Query(1),
):
    with tx() as conn:
        ok, _admin = token_verify_admin(conn, token)
        if ok <= 0:
            return vo(-1)

        offset = (page_number - 1) * page_size
        name_pattern = f"%{name}%"
        title_pattern = f"%{title}%"
        count = fetch_one(
            conn,
            "select count(*) as c from staff_action_view where staff_name like :name_pattern and action_title like :title_pattern",
            {"name_pattern": name_pattern, "title_pattern": title_pattern},
        )
        rows = fetch_all(
            conn,
            "select * from staff_action_view where staff_name like :name_pattern and action_title like :title_pattern order by id DESC limit :ps offset :off",
            {"name_pattern": name_pattern, "title_pattern": title_pattern, "ps": page_size, "off": offset},
        )
        return vo(int(count["c"]) if count else 0, rows)
