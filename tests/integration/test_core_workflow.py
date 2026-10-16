"""Exercise the member-to-staff path against a real disposable SQLite schema."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app
from app.passwords import hash_password


def test_login_enroll_start_and_sign(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'workflow.sqlite3'}")
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
        conn.execute(
            text("insert into users(username, password, name, state) values (:u, :p, :n, :s)"),
            {"u": "member01", "p": hash_password("Aa1$abcd"), "n": "Member", "s": 2},
        )
        conn.execute(
            text("insert into users(username, password, name, state) values (:u, :p, :n, :s)"),
            {"u": "staff01", "p": hash_password("Aa1$abcd"), "n": "Staff", "s": 3},
        )
        staff_id = conn.execute(text("select id from users where username='staff01'")).scalar_one()
        conn.execute(
            text(
                "insert into actions(title, state, max_num, staff_user_id, open_time, close_time) "
                "values (:title, 2, 4, :staff, :opened, :closed)"
            ),
            {
                "title": "Demo Session",
                "staff": staff_id,
                "opened": datetime.now() - timedelta(hours=1),
                "closed": datetime.now() + timedelta(hours=1),
            },
        )
        action_id = conn.execute(text("select id from actions where title='Demo Session'")).scalar_one()

    monkeypatch.setattr(db_module, "engine", engine)
    client = TestClient(app)

    def login(username):
        response = client.post("/api/user/login", json={"username": username, "password": "Aa1$abcd"})
        assert response.status_code == 200
        assert response.json()["status"] in (2, 3)
        return {"Authorization": f"Bearer {response.json()['data']}"}

    member_headers = login("member01")
    staff_headers = login("staff01")

    assert client.post("/api/user/verify", headers=member_headers).json()["status"] == 1
    assert client.post("/api/action/queryAction", headers=member_headers).json()["status"] == 1
    enroll = client.post(f"/api/action/attendAction?action_id={action_id}", headers=member_headers)
    assert enroll.json()["status"] == 3
    assert client.post(f"/api/action/attendAction?action_id={action_id}", headers=member_headers).json()["status"] == 1

    records = client.post("/api/action/queryRecord", headers=member_headers).json()
    assert records["status"] == 1
    assert len(records["data"]) == 1
    code = records["data"][0]["sign_code"]

    # Starting check-in is only permitted after the activity enters state 3.
    assert client.post(f"/api/staff/startSign?action_id={action_id}", headers=staff_headers).json()["status"] == 1
    with engine.begin() as conn:
        conn.execute(text("update actions set state=3 where id=:id"), {"id": action_id})
    assert client.post(f"/api/staff/startSign?action_id={action_id}", headers=staff_headers).json()["status"] == 4
    assert client.post("/api/staff/querySign", headers=staff_headers, json={"sign_code": code}).json()["status"] == 5
    assert client.post("/api/staff/finishSign", headers=staff_headers, json={"sign_code": code}).json()["status"] == 5
    assert client.post("/api/staff/finishSign", headers=staff_headers, json={"sign_code": code}).json()["status"] == 1
    assert client.post("/api/action/queryRecord", headers=member_headers).json()["data"][0]["state"] == 1
