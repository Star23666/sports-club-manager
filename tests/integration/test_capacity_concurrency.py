"""Concurrent requests against a disposable SQLite file, not an in-memory mock."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import db as db_module
from app.db_schema import SCHEMA_DDL
from app.main import app


def test_parallel_enrollment_cannot_overbook_and_waiting_rank_is_unique(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'capacity.sqlite3'}", connect_args={"check_same_thread": False})
    tokens = [f"capacity-token-{index}" for index in range(6)]
    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            conn.execute(text(statement))
        for index, token in enumerate(tokens):
            conn.execute(
                text("insert into users(username, password, state) values (:username, 'test-only', 2)"),
                {"username": f"member-{index}"},
            )
            user_id = conn.execute(
                text("select id from users where username=:username"), {"username": f"member-{index}"}
            ).scalar_one()
            conn.execute(
                text("insert into tokens(user_id, token, out_time) values (:uid, :token, :expires)"),
                {"uid": user_id, "token": token, "expires": datetime.now() + timedelta(hours=1)},
            )
        conn.execute(text("insert into actions(title, state, max_num) values ('one seat', 2, 1)"))
        action_id = conn.execute(text("select id from actions where title='one seat'")).scalar_one()

    monkeypatch.setattr(db_module, "engine", engine)

    def parallel_requests(path, selected_tokens):
        barrier = Barrier(len(selected_tokens))

        def request(token):
            with TestClient(app) as client:
                barrier.wait(timeout=10)
                response = client.post(path, headers={"Authorization": f"Bearer {token}"})
                assert response.status_code == 200
                return token, response.json()["status"]

        with ThreadPoolExecutor(max_workers=len(selected_tokens)) as pool:
            return list(pool.map(request, selected_tokens))

    enrollments = parallel_requests(f"/api/action/attendAction?action_id={action_id}", tokens)
    assert sorted(status for _, status in enrollments) == [2, 2, 2, 2, 2, 3]
    winner = next(token for token, status in enrollments if status == 3)
    losers = [token for token, status in enrollments if status == 2]

    waiting = parallel_requests(f"/api/waiting/waitCreate?action_id={action_id}", losers)
    assert all(status == 3 for _, status in waiting)
    with engine.begin() as conn:
        assert conn.execute(text("select count(*) from records where action_id=:aid"), {"aid": action_id}).scalar_one() == 1
        ranks = conn.execute(text("select rank from waiting where action_id=:aid order by rank"), {"aid": action_id}).scalars().all()
        assert ranks == [1, 2, 3, 4, 5]
        winner_record = conn.execute(
            text("select r.id from records r join tokens t on t.user_id=r.user_id where t.token=:token"),
            {"token": winner},
        ).scalar_one()

    with TestClient(app) as client:
        cancel = client.post(
            f"/api/action/cancelAction?record_id={winner_record}",
            headers={"Authorization": f"Bearer {winner}"},
        )
    assert cancel.json()["status"] == 2
    with engine.begin() as conn:
        assert conn.execute(text("select count(*) from records where action_id=:aid"), {"aid": action_id}).scalar_one() == 1
        ranks = conn.execute(text("select rank from waiting where action_id=:aid order by rank"), {"aid": action_id}).scalars().all()
        assert ranks == [1, 2, 3, 4]
