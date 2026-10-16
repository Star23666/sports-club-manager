"""Opt-in live MySQL check-in/completion race on a disposable database."""

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
    os.getenv("TEST_MYSQL_CHECKIN") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
@pytest.mark.parametrize(
    ("stop_path", "stop_role", "stop_status"),
    [
        ("/api/staff/stopAction", "staff", 4),
        ("/admin/api/action/stopAction", "admin", 1),
    ],
)
def test_mysql_parallel_checkin_and_completion(stop_path, stop_role, stop_status):
    if not settings.db_name.startswith("club_checkin_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    run_id = uuid4().hex[:8]
    tokens = {role: f"checkin-{run_id}-{role}" for role in ("staff", "admin", "member")}
    with tx() as conn:
        user_ids = {}
        for role, state in (("staff", 3), ("admin", 4), ("member", 2)):
            username = f"checkin-{run_id}-{role}"
            exec_one(
                conn, "insert into users(username, password, state) values (:name, 'test-only', :state)",
                {"name": username, "state": state},
            )
            user_ids[role] = fetch_one(
                conn, "select ID from users where username=:name", {"name": username},
            )["id"]
            exec_one(
                conn, "insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)",
                {"uid": user_ids[role], "token": tokens[role], "expiry": datetime.now() + timedelta(hours=1)},
            )
        title = f"checkin-race-{run_id}"
        code = f"checkin-code-{run_id}"
        exec_one(
            conn, "insert into actions(title, state, staff_user_id) values (:title, 4, :staff)",
            {"title": title, "staff": user_ids["staff"]},
        )
        action_id = fetch_one(conn, "select ID from actions where title=:title", {"title": title})["id"]
        exec_one(
            conn, "insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, :code, 0)",
            {"uid": user_ids["member"], "aid": action_id, "code": code},
        )

    barrier = Barrier(2)

    def request(path, role, *, json=None):
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                path, params={"action_id": action_id} if json is None else None,
                json=json, headers={"Authorization": f"Bearer {tokens[role]}"},
            )
            assert response.status_code == 200
            return response.json()["status"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        sign_future = pool.submit(request, "/api/staff/finishSign", "staff", json={"sign_code": code})
        stop_future = pool.submit(request, stop_path, stop_role)
        sign_status, completion_status = sign_future.result(), stop_future.result()

    assert completion_status == stop_status
    assert sign_status in (4, 5)
    with tx() as conn:
        record = fetch_one(conn, "select state from records where sign_code=:code", {"code": code})
        member = fetch_one(conn, "select unsigned_num from users where ID=:uid", {"uid": user_ids["member"]})
        action = fetch_one(conn, "select state from actions where ID=:aid", {"aid": action_id})
    assert action["state"] == 5
    assert (record["state"], member["unsigned_num"]) == ((1, 0) if sign_status == 5 else (0, 1))
