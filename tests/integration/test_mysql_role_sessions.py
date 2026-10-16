"""Opt-in role-transition session checks on a disposable MySQL database."""

import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db import DB_IS_SQLITE, exec_one, fetch_one, tx
from app.main import app
from app.passwords import hash_password
from app.settings import settings


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_ROLES") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
def test_mysql_role_promotion_and_absence_revoke_sessions():
    if not settings.db_name.startswith("club_role_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    run_id = uuid4().hex[:8]

    def add_user(conn, suffix, state, unsigned=0):
        name = f"role-{run_id}-{suffix}"
        token = f"role-token-{run_id}-{suffix}"
        exec_one(
            conn, "insert into users(username, password, state, unsigned_num) values (:name, :password, :state, :unsigned)",
            {"name": name, "password": hash_password("Aa1$oldpass"), "state": state, "unsigned": unsigned},
        )
        user_id = fetch_one(conn, "select ID from users where username=:name", {"name": name})["id"]
        exec_one(
            conn, "insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)",
            {"uid": user_id, "token": token, "expiry": datetime.now() + timedelta(hours=1)},
        )
        return name, user_id, token

    with tx() as conn:
        _, _, admin_token = add_user(conn, "admin", 4)
        _, staff_id, staff_token = add_user(conn, "staff", 3)
        promoted_name, promoted_id, promoted_token = add_user(conn, "promoted", 2)
        _, absent_id, absent_token = add_user(conn, "absent", 2, unsigned=2)
        exec_one(
            conn, "insert into actions(title, state, staff_user_id) values (:title, 4, :staff)",
            {"title": f"role-action-{run_id}", "staff": staff_id},
        )
        action_id = fetch_one(conn, "select ID from actions where title=:title", {"title": f"role-action-{run_id}"})["id"]
        exec_one(
            conn, "insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, :code, 0)",
            {"uid": absent_id, "aid": action_id, "code": f"role-code-{run_id}"},
        )

    with TestClient(app) as client:
        promoted = client.post(
            "/admin/api/member/updateUserInf", params={"id": promoted_id},
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": promoted_name, "state": 3, "name": "Promoted", "student_id": "S1",
                "card_id": "C1", "phone": "", "wechat_id": "", "email": "",
            },
        )
        assert promoted.json()["status"] == 3
        assert client.post(
            "/api/user/verify", headers={"Authorization": f"Bearer {promoted_token}"}
        ).json()["status"] == -1

        stopped = client.post(
            "/api/staff/stopAction", params={"action_id": action_id},
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert stopped.json()["status"] == 4
        assert client.post(
            "/api/user/verify", headers={"Authorization": f"Bearer {absent_token}"}
        ).json()["status"] == -1
        assert client.post(
            "/admin/api/user/verify", headers={"Authorization": f"Bearer {admin_token}"}
        ).json()["status"] == 1
