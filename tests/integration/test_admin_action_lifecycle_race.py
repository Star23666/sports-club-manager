"""Admin action transitions share the lock used by member and staff operations."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app


def seed(tmp_path, monkeypatch, state):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'lifecycle.sqlite3'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
        ids = {}
        for role, role_state in (("admin", 4), ("staff", 3), ("member", 2)):
            conn.execute(
                text("insert into users(username, password, state) values (:role, 'test-only', :state)"),
                {"role": role, "state": role_state},
            )
            ids[role] = conn.execute(
                text("select id from users where username=:role"), {"role": role},
            ).scalar_one()
            conn.execute(
                text("insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)"),
                {"uid": ids[role], "token": f"{role}-token", "expiry": datetime.now() + timedelta(hours=1)},
            )
        conn.execute(
            text("insert into actions(title, place, time_range, date, max_num, state, staff_user_id) "
                 "values ('event', '', '', '', 0, :state, :staff)"),
            {"state": state, "staff": ids["staff"]},
        )
        action_id = conn.execute(text("select id from actions where title='event'")).scalar_one()
    monkeypatch.setattr(db_module, "engine", engine)
    return engine, ids, action_id


def race_requests(first, second):
    barrier = Barrier(2)

    def run(request):
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            return request(client)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(run, first)
        second_future = pool.submit(run, second)
        return first_future.result(), second_future.result()


def post(client, path, role, *, params=None):
    response = client.post(path, params=params, headers={"Authorization": f"Bearer {role}-token"})
    assert response.status_code == 200
    return response.json()["status"]


def test_closing_registration_cannot_leave_a_late_waiting_entry(tmp_path, monkeypatch):
    engine, _, action_id = seed(tmp_path, monkeypatch, state=2)
    wait_status, stop_status = race_requests(
        lambda client: post(client, "/api/waiting/waitCreate", "member", params={"action_id": action_id}),
        lambda client: post(client, "/admin/api/action/stopRegisterAction", "admin", params={"action_id": action_id}),
    )
    assert wait_status in (0, 3)
    assert stop_status == 1
    with engine.begin() as conn:
        assert conn.execute(text("select state from actions where id=:id"), {"id": action_id}).scalar_one() == 3
        assert conn.execute(text("select count(*) from waiting where action_id=:id"), {"id": action_id}).scalar_one() == 0


def test_edit_cannot_rewind_started_checkin(tmp_path, monkeypatch):
    engine, ids, action_id = seed(tmp_path, monkeypatch, state=3)
    update_params = {
        "id": action_id, "title": "event", "place": "", "time_range": "", "date": "",
        "max_num": 0, "open_time": "", "close_time": "", "staff_user_id": ids["staff"],
        "wechat_url": "",
    }
    update_status, start_status = race_requests(
        lambda client: post(client, "/admin/api/action/update", "admin", params=update_params),
        lambda client: post(client, "/api/staff/startSign", "staff", params={"action_id": action_id}),
    )
    assert update_status in (1, 4)
    assert start_status == 4
    with engine.begin() as conn:
        assert conn.execute(text("select state from actions where id=:id"), {"id": action_id}).scalar_one() == 4
