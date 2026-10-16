"""Check-in and action completion must agree on whether a member was absent."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app


@pytest.mark.parametrize(
    ("stop_path", "stop_token", "stop_status"),
    [
        ("/api/staff/stopAction", "staff-token", 4),
        ("/admin/api/action/stopAction", "admin-token", 1),
    ],
)
def test_parallel_checkin_and_completion_keep_absence_consistent(
    tmp_path, monkeypatch, stop_path, stop_token, stop_status,
):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'checkin-race.sqlite3'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
        for username, state, token in (
            ("staff", 3, "staff-token"),
            ("admin", 4, "admin-token"),
            ("member", 2, "member-token"),
        ):
            conn.execute(
                text("insert into users(username, password, state) values (:name, 'test-only', :state)"),
                {"name": username, "state": state},
            )
            user_id = conn.execute(
                text("select id from users where username=:name"), {"name": username},
            ).scalar_one()
            conn.execute(
                text("insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)"),
                {"uid": user_id, "token": token, "expiry": datetime.now() + timedelta(hours=1)},
            )
        staff_id = conn.execute(text("select id from users where username='staff'")).scalar_one()
        member_id = conn.execute(text("select id from users where username='member'")).scalar_one()
        conn.execute(
            text("insert into actions(title, state, staff_user_id) values ('race', 4, :staff)"),
            {"staff": staff_id},
        )
        action_id = conn.execute(text("select id from actions where title='race'")).scalar_one()
        conn.execute(
            text("insert into records(user_id, action_id, sign_code, state) "
                 "values (:member, :action, 'race-code', 0)"),
            {"member": member_id, "action": action_id},
        )

    monkeypatch.setattr(db_module, "engine", engine)
    barrier = Barrier(2)

    def check_in():
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                "/api/staff/finishSign", headers={"Authorization": "Bearer staff-token"},
                json={"sign_code": "race-code"},
            )
            assert response.status_code == 200
            return response.json()["status"]

    def complete():
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                stop_path, params={"action_id": action_id},
                headers={"Authorization": f"Bearer {stop_token}"},
            )
            assert response.status_code == 200
            return response.json()["status"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        sign_future = pool.submit(check_in)
        stop_future = pool.submit(complete)
        sign_status, completion_status = sign_future.result(), stop_future.result()

    assert completion_status == stop_status
    assert sign_status in (4, 5)
    with engine.begin() as conn:
        record_state = conn.execute(text("select state from records where sign_code='race-code'")).scalar_one()
        unsigned = conn.execute(
            text("select unsigned_num from users where id=:uid"), {"uid": member_id},
        ).scalar_one()
        action_state = conn.execute(
            text("select state from actions where id=:aid"), {"aid": action_id},
        ).scalar_one()
    assert action_state == 5
    assert (record_state, unsigned) == ((1, 0) if sign_status == 5 else (0, 1))
