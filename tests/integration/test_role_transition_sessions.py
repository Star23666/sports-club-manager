"""Role/status changes must not silently upgrade an existing bearer token."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app
from app.passwords import hash_password


@pytest.fixture
def role_db(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'roles.sqlite3'}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
    monkeypatch.setattr(db_module, "engine", engine)
    return engine


def add_user(conn, username, state, token, unsigned_num=0):
    conn.execute(
        text("insert into users(username, password, state, unsigned_num) values (:name, :password, :state, :unsigned)"),
        {"name": username, "password": hash_password("Aa1$oldpass"), "state": state, "unsigned": unsigned_num},
    )
    user_id = conn.execute(text("select id from users where username=:name"), {"name": username}).scalar_one()
    conn.execute(
        text("insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)"),
        {"uid": user_id, "token": token, "expiry": datetime.now() + timedelta(hours=1)},
    )
    return user_id


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def edit_user(client, user_id, state):
    return client.post(
        "/admin/api/member/updateUserInf",
        params={"id": user_id},
        headers=auth("admin-token"),
        json={
            "username": "member", "state": state, "name": "Member", "student_id": "S1",
            "card_id": "C1", "phone": "", "wechat_id": "", "email": "",
        },
    ).json()["status"]


def test_promotion_revokes_old_token_but_same_state_edit_does_not(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        member_id = add_user(conn, "member", 2, "member-old-token")

    with TestClient(app) as client:
        assert edit_user(client, member_id, 2) == 3
        assert client.post("/api/user/verify", headers=auth("member-old-token")).json()["status"] == 1
        assert edit_user(client, member_id, 3) == 3
        assert client.post("/api/user/verify", headers=auth("member-old-token")).json()["status"] == -1
        assert client.post("/api/staff/queryAction", headers=auth("member-old-token")).json()["status"] == -2
        assert client.post("/admin/api/user/verify", headers=auth("admin-token")).json()["status"] == 1

        login = client.post("/api/user/login", json={"username": "member", "password": "Aa1$oldpass"}).json()
        assert login["status"] == 3
        assert client.post("/api/staff/queryAction", headers=auth(login["data"])).json()["status"] == 1
        assert edit_user(client, member_id, 2) == 3
        assert client.post("/api/user/verify", headers=auth(login["data"])).json()["status"] == -1


def test_admin_review_and_credit_restoration_revoke_old_tokens(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        restricted_id = add_user(conn, "restricted", 1, "restricted-token")
        pending_id = add_user(conn, "pending", -1, "pending-token")

    with TestClient(app) as client:
        assert client.post(
            "/admin/api/member/clearUserUnsigned", params={"user_id": restricted_id}, headers=auth("admin-token")
        ).json()["status"] == 2
        assert client.post("/api/user/verify", headers=auth("restricted-token")).json()["status"] == -1
        assert client.post(
            "/admin/api/member/passUser", params={"user_id": pending_id}, headers=auth("admin-token")
        ).json()["status"] == 1
        with role_db.begin() as conn:
            assert conn.execute(text("select count(*) from tokens where user_id=:uid"), {"uid": pending_id}).scalar_one() == 0


def test_recalculating_absences_revokes_session_if_member_becomes_restricted(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        member_id = add_user(conn, "member", 2, "member-token")
        for index in range(3):
            conn.execute(
                text("insert into actions(title, state) values (:title, 5)"),
                {"title": f"past-{index}"},
            )
            action_id = conn.execute(text("select id from actions where title=:title"), {"title": f"past-{index}"}).scalar_one()
            conn.execute(
                text("insert into records(user_id, action_id, state) values (:uid, :aid, 0)"),
                {"uid": member_id, "aid": action_id},
            )

    with TestClient(app) as client:
        assert client.post(
            "/admin/api/member/resetUserUnsigned", params={"user_id": member_id}, headers=auth("admin-token")
        ).json()["status"] == 2
        assert client.post("/api/user/verify", headers=auth("member-token")).json()["status"] == -1
    with role_db.begin() as conn:
        assert conn.execute(text("select state from users where id=:uid"), {"uid": member_id}).scalar_one() == 1


@pytest.mark.parametrize(
    ("path", "staff_state", "expected"),
    [("/admin/api/action/stopAction", 4, 1), ("/api/staff/stopAction", 3, 4)],
)
def test_finishing_action_revokes_newly_restricted_member_token(role_db, path, staff_state, expected):
    with role_db.begin() as conn:
        operator_id = add_user(conn, "operator", staff_state, "operator-token")
        member_id = add_user(conn, "member", 2, "member-token", unsigned_num=2)
        conn.execute(
            text("insert into actions(title, state, staff_user_id) values ('finished event', 4, :staff)"),
            {"staff": operator_id},
        )
        action_id = conn.execute(text("select id from actions where title='finished event'")).scalar_one()
        conn.execute(
            text("insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, 'code', 0)"),
            {"uid": member_id, "aid": action_id},
        )

    with TestClient(app) as client:
        assert client.post(path, params={"action_id": action_id}, headers=auth("operator-token")).json()["status"] == expected
        assert client.post("/api/user/verify", headers=auth("member-token")).json()["status"] == -1
    with role_db.begin() as conn:
        assert conn.execute(text("select state from users where id=:uid"), {"uid": member_id}).scalar_one() == 1


def test_resigning_restores_member_but_revokes_restricted_session(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        member_id = add_user(conn, "member", 1, "restricted-token", unsigned_num=3)
        conn.execute(text("insert into actions(title, state) values ('finished event', 5)"))
        action_id = conn.execute(text("select id from actions where title='finished event'")).scalar_one()
        conn.execute(
            text("insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, 'late-code', 0)"),
            {"uid": member_id, "aid": action_id},
        )
        record_id = conn.execute(text("select id from records where sign_code='late-code'")).scalar_one()

    with TestClient(app) as client:
        assert client.post(
            "/admin/api/action/reSign", params={"record_id": record_id},
            headers=auth("admin-token"), json={"sign_code": "late-code"},
        ).json()["status"] == 2
        assert client.post("/api/user/verify", headers=auth("restricted-token")).json()["status"] == -1
    with role_db.begin() as conn:
        assert conn.execute(text("select state from users where id=:uid"), {"uid": member_id}).scalar_one() == 2


def test_credit_actions_do_not_unban_an_account(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        banned_id = add_user(conn, "banned", 0, "banned-token", unsigned_num=3)
        add_user(conn, "restricted", 1, "restricted-token", unsigned_num=3)
        add_user(conn, "normal", 2, "normal-token")
        conn.execute(text("update users set name=username, student_id=username where username in ('restricted', 'normal')"))

    with TestClient(app) as client:
        for path in ("clearUserUnsigned", "resetUserUnsigned"):
            result = client.post(
                f"/admin/api/member/{path}", params={"user_id": banned_id},
                headers=auth("admin-token"),
            ).json()
            assert result["status"] == 1
            assert result["data"] == "User Kind Not Match"

        listed = client.post(
            "/admin/api/member/queryUnsignedMembers", headers=auth("admin-token"),
            json={"name": "", "student_id": ""},
        ).json()
        assert listed["status"] == 2
        assert {member["username"] for member in listed["data"]} == {"restricted", "normal"}

    with role_db.begin() as conn:
        state, unsigned = conn.execute(
            text("select state, unsigned_num from users where id=:uid"), {"uid": banned_id},
        ).one()
        assert (state, unsigned) == (0, 3)


def test_account_review_cannot_approve_a_banned_account(role_db):
    with role_db.begin() as conn:
        add_user(conn, "admin", 4, "admin-token")
        banned_id = add_user(conn, "banned", 0, "banned-token")
        pending_id = add_user(conn, "pending", -1, "pending-token")

    with TestClient(app) as client:
        denied = client.post(
            "/admin/api/member/passUser", params={"user_id": banned_id},
            headers=auth("admin-token"),
        ).json()
        assert denied["status"] == 0
        assert client.post(
            "/admin/api/member/passUser", params={"user_id": pending_id},
            headers=auth("admin-token"),
        ).json()["status"] == 1

    with role_db.begin() as conn:
        assert conn.execute(text("select state from users where id=:uid"), {"uid": banned_id}).scalar_one() == 0
        assert conn.execute(text("select state from users where id=:uid"), {"uid": pending_id}).scalar_one() == 2
