"""Opt-in prelaunch check against a disposable, freshly seeded MySQL database.

Apply ``database/install.sql`` and run ``python/seed_demo.py`` first. This test
modifies only a database whose name starts with ``club_e2e_test``.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.db import DB_IS_SQLITE, tx, fetch_one, exec_one
from app.main import app
from app.settings import settings


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_WORKFLOW") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
def test_mysql_member_to_staff_and_authorization():
    if not settings.db_name.startswith("club_e2e_test"):
        pytest.fail("refusing to test against a non-disposable MySQL database")

    with tx() as conn:
        action = fetch_one(conn, "select * from actions where title='Tuesday Night Session' order by ID desc limit 1")
        assert action is not None
        action_id = action["id"]
        # The demo seed assigns this activity to the first staff member.
        owner = fetch_one(conn, "select username from users where ID=:id", {"id": action["staff_user_id"]})
        assert owner is not None

    client = TestClient(app)

    def login(username):
        response = client.post("/api/user/login", json={"username": username, "password": "Aa1$abcd"})
        assert response.status_code == 200
        assert response.json()["status"] in (2, 3)
        return {"Authorization": f"Bearer {response.json()['data']}"}

    member = login("zhangsan")
    other_member = login("lisi")
    staff = login(owner["username"])
    other_staff = login("staff02" if owner["username"] == "staff01" else "staff01")

    assert client.post("/api/staff/queryAction", headers=member).json()["status"] == -1
    assert client.post(f"/api/staff/startSign?action_id={action_id}", headers=other_staff).json()["status"] != 4
    assert client.post(f"/api/action/attendAction?action_id={action_id}", headers=member).json()["status"] == 3
    assert client.post(f"/api/action/attendAction?action_id={action_id}", headers=member).json()["status"] == 1

    record = client.post("/api/action/queryRecord", headers=member).json()["data"][0]
    code = record["sign_code"]
    record_id = record["id"]
    assert client.post("/api/action/queryRecord", headers=other_member).json()["data"] == []
    assert client.post(f"/api/action/queryWechatGroup?record_id={record_id}", headers=other_member).json()["status"] == 0
    assert client.post(f"/api/action/cancelAction?record_id={record_id}", headers=other_member).json()["status"] == 1

    with tx() as conn:
        exec_one(conn, "update actions set state=3 where ID=:id", {"id": action_id})
    assert client.post(f"/api/staff/startSign?action_id={action_id}", headers=other_staff).json()["status"] == 2
    assert client.post(f"/api/staff/startSign?action_id={action_id}", headers=staff).json()["status"] == 4
    with tx() as conn:
        sender = fetch_one(conn, "select ID from users where username='zhangsan'")
        receiver = fetch_one(conn, "select ID from users where username='lisi'")
        exec_one(
            conn,
            "insert into transfer(record_id, send_user_id, receive_user_id) values (:rid, :sid, :uid)",
            {"rid": record_id, "sid": sender["id"], "uid": receiver["id"]},
        )
        stale_transfer = fetch_one(conn, "select ID from transfer where record_id=:rid", {"rid": record_id})
    assert client.post(
        f"/api/transfer/acceptTransfer?transfer_id={stale_transfer['id']}", headers=other_member
    ).json()["status"] == 0
    with tx() as conn:
        assert fetch_one(conn, "select user_id from records where ID=:id", {"id": record_id})["user_id"] == sender["id"]
        exec_one(conn, "delete from transfer where ID=:id", {"id": stale_transfer["id"]})
    assert client.post("/api/staff/querySign", headers=other_staff, json={"sign_code": code}).json()["status"] == 2
    assert client.post("/api/staff/querySign", headers=staff, json={"sign_code": code}).json()["status"] == 5
    assert client.post("/api/staff/finishSign", headers=staff, json={"sign_code": code}).json()["status"] == 5
    assert client.post("/api/staff/finishSign", headers=staff, json={"sign_code": code}).json()["status"] == 1
    assert client.post("/api/action/queryRecord", headers=member).json()["data"][0]["state"] == 1
