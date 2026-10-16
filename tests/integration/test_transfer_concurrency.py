"""Transfer authorization and races against a disposable SQLite database."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app


def test_public_transfer_can_only_be_claimed_once(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'transfer.sqlite3'}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
        for name, state in (("sender", 2), ("receiver-a", 2), ("receiver-b", 2), ("restricted", 1)):
            conn.execute(
                text("insert into users(username, password, state) values (:name, 'test-only', :state)"),
                {"name": name, "state": state},
            )
            user_id = conn.execute(text("select id from users where username=:name"), {"name": name}).scalar_one()
            conn.execute(
                text("insert into tokens(user_id, token, out_time) values (:id, :token, :expiry)"),
                {"id": user_id, "token": f"token-{name}", "expiry": datetime.now() + timedelta(hours=1)},
            )
        conn.execute(text("insert into actions(title, state, max_num) values ('transfer race', 3, 1)"))
        action_id = conn.execute(text("select id from actions where title='transfer race'")).scalar_one()
        sender_id = conn.execute(text("select id from users where username='sender'")).scalar_one()
        conn.execute(
            text("insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, 'old-code', 0)"),
            {"uid": sender_id, "aid": action_id},
        )
        record_id = conn.execute(text("select id from records where action_id=:aid"), {"aid": action_id}).scalar_one()

    monkeypatch.setattr(db_module, "engine", engine)

    def post(path, name, body=None):
        with TestClient(app) as client:
            response = client.post(path, headers={"Authorization": f"Bearer token-{name}"}, json=body)
        assert response.status_code == 200
        return response.json()["status"]

    create_path = f"/api/transfer/transferRecord?record_id={record_id}"
    assert post(create_path, "sender", {"receive_user": ""}) == 4
    assert post(create_path, "sender", {"receive_user": ""}) == 2
    with engine.begin() as conn:
        transfer_id = conn.execute(text("select id from transfer where record_id=:rid"), {"rid": record_id}).scalar_one()

    accept_path = f"/api/transfer/acceptTransfer?transfer_id={transfer_id}"
    assert post(accept_path, "restricted") == 0
    barrier = Barrier(2)

    def claim(name):
        barrier.wait(timeout=10)
        return name, post(accept_path, name)

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(claim, ("receiver-a", "receiver-b")))
    assert sorted(status for _, status in outcomes) == [-1, 2]
    winner = next(name for name, status in outcomes if status == 2)
    with engine.begin() as conn:
        assert conn.execute(text("select count(*) from transfer")).scalar_one() == 0
        owner = conn.execute(
            text("select u.username from records r join users u on u.id=r.user_id where r.id=:id"),
            {"id": record_id},
        ).scalar_one()
        assert owner == winner
        assert conn.execute(text("select sign_code from records where id=:id"), {"id": record_id}).scalar_one() != "old-code"

    # A named transfer remains private: only its intended recipient may act.
    with engine.begin() as conn:
        conn.execute(text("insert into actions(title, state, max_num) values ('private transfer', 3, 1)"))
        private_action = conn.execute(text("select id from actions where title='private transfer'")).scalar_one()
        conn.execute(
            text("insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, 'private-code', 0)"),
            {"uid": sender_id, "aid": private_action},
        )
        private_record = conn.execute(
            text("select id from records where action_id=:aid"), {"aid": private_action}
        ).scalar_one()
    assert post(f"/api/transfer/transferRecord?record_id={private_record}", "sender", {"receive_user": "receiver-a"}) == 4
    with engine.begin() as conn:
        private_transfer = conn.execute(
            text("select id from transfer where record_id=:rid"), {"rid": private_record}
        ).scalar_one()
    private_accept = f"/api/transfer/acceptTransfer?transfer_id={private_transfer}"
    private_refuse = f"/api/transfer/refuseTransfer?transfer_id={private_transfer}"
    assert post(private_accept, "receiver-b") == 0
    assert post(private_refuse, "receiver-b") == 0
    assert post(private_accept, "receiver-a") == 2
