"""Opt-in admin/member/staff lifecycle races on a disposable MySQL database."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db import DB_IS_SQLITE, exec_one, fetch_one, tx
from app.main import app
from app.settings import settings


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_ADMIN_LIFECYCLE") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
@pytest.mark.parametrize("initial_state", [2, 3])
def test_mysql_admin_transition_serializes_with_member_or_staff(initial_state):
    if not settings.db_name.startswith("club_lifecycle_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    run_id = uuid4().hex[:8]
    tokens = {role: f"lifecycle-{run_id}-{role}" for role in ("admin", "staff", "member")}
    with tx() as conn:
        ids = {}
        for role, state in (("admin", 4), ("staff", 3), ("member", 2)):
            name = f"lifecycle-{run_id}-{role}"
            exec_one(
                conn, "insert into users(username, password, state) values (:name, 'test-only', :state)",
                {"name": name, "state": state},
            )
            ids[role] = fetch_one(conn, "select ID from users where username=:name", {"name": name})["id"]
            exec_one(
                conn, "insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)",
                {"uid": ids[role], "token": tokens[role], "expiry": datetime.now() + timedelta(hours=1)},
            )
        title = f"lifecycle-event-{run_id}"
        exec_one(
            conn, "insert into actions(title, place, time_range, `date`, max_num, state, staff_user_id) "
                  "values (:title, '', '', '', 0, :state, :staff)",
            {"title": title, "state": initial_state, "staff": ids["staff"]},
        )
        action_id = fetch_one(conn, "select ID from actions where title=:title", {"title": title})["id"]

    barrier = Barrier(2)

    def request(path, role, params):
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                path, params=params, headers={"Authorization": f"Bearer {tokens[role]}"},
            )
            assert response.status_code == 200
            return response.json()["status"]

    if initial_state == 2:
        first = ("/api/waiting/waitCreate", "member", {"action_id": action_id})
        second = ("/admin/api/action/stopRegisterAction", "admin", {"action_id": action_id})
    else:
        first = ("/admin/api/action/update", "admin", {
            "id": action_id, "title": title, "place": "", "time_range": "", "date": "",
            "max_num": 0, "open_time": "", "close_time": "", "staff_user_id": ids["staff"],
            "wechat_url": "",
        })
        second = ("/api/staff/startSign", "staff", {"action_id": action_id})

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(request, *first)
        second_future = pool.submit(request, *second)
        first_status, second_status = first_future.result(), second_future.result()

    with tx() as conn:
        action = fetch_one(conn, "select state from actions where ID=:id", {"id": action_id})
        waiting = fetch_one(conn, "select count(*) as c from waiting where action_id=:id", {"id": action_id})
    if initial_state == 2:
        assert first_status in (0, 3)
        assert second_status == 1
        assert action["state"] == 3
        assert waiting["c"] == 0
    else:
        assert first_status in (1, 4)
        assert second_status == 4
        assert action["state"] == 4
