"""Opt-in parallel capacity check on a freshly installed disposable MySQL DB."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db import DB_IS_SQLITE, exec_one, fetch_all, fetch_one, tx
from app.main import app
from app.rate_limit import allow_login_attempt, clear_login_account_attempts
from app.settings import settings


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_CAPACITY") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
def test_mysql_parallel_enrollment_and_waitlist():
    if not settings.db_name.startswith("club_capacity_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    run_id = uuid4().hex[:8]
    tokens = [f"capacity-test-token-{run_id}-{index}" for index in range(6)]
    with tx() as conn:
        for index, token in enumerate(tokens):
            exec_one(
                conn, "insert into users(username, password, state) values (:username, 'test-only', 2)",
                {"username": f"capacity-test-member-{run_id}-{index}"},
            )
            user = fetch_one(conn, "select ID from users where username=:username", {"username": f"capacity-test-member-{run_id}-{index}"})
            exec_one(
                conn, "insert into tokens(user_id, token, out_time) values (:uid, :token, :expires)",
                {"uid": user["id"], "token": token, "expires": datetime.now() + timedelta(hours=1)},
            )
        exec_one(conn, "insert into actions(title, state, max_num) values (:title, 2, 1)", {"title": f"capacity test {run_id}"})
        action = fetch_one(conn, "select ID from actions where title=:title", {"title": f"capacity test {run_id}"})
        action_id = action["id"]

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
    with tx() as conn:
        records = fetch_all(conn, "select ID from records where action_id=:aid", {"aid": action_id})
        ranks = fetch_all(conn, "select `rank` from waiting where action_id=:aid order by `rank`", {"aid": action_id})
    assert len(records) == 1
    assert [row["rank"] for row in ranks] == [1, 2, 3, 4, 5]

    with tx() as conn:
        winner_record = fetch_one(
            conn,
            "select r.ID from records r join tokens t on t.user_id=r.user_id where t.token=:token",
            {"token": winner},
        )
    with TestClient(app) as client:
        cancel = client.post(
            f"/api/action/cancelAction?record_id={winner_record['id']}",
            headers={"Authorization": f"Bearer {winner}"},
        )
    assert cancel.json()["status"] == 2
    with tx() as conn:
        records = fetch_all(conn, "select ID from records where action_id=:aid", {"aid": action_id})
        ranks = fetch_all(conn, "select `rank` from waiting where action_id=:aid order by `rank`", {"aid": action_id})
    assert len(records) == 1
    assert [row["rank"] for row in ranks] == [1, 2, 3, 4]


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_CAPACITY") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
def test_mysql_login_counter_resets_after_window_and_success():
    if not settings.db_name.startswith("club_capacity_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    results = []
    for attempt in range(3):
        with tx() as conn:
            results.append(allow_login_attempt(
                conn, scope="login-account", subject="mysql-capacity-test", limit=2,
                window_seconds=60, now=120 + attempt,
            ))
    assert results == [True, True, False]

    with tx() as conn:
        assert allow_login_attempt(
            conn, scope="login-account", subject="mysql-capacity-test", limit=2,
            window_seconds=60, now=180,
        )
        clear_login_account_attempts(conn, "MYSQL-CAPACITY-TEST")
    with tx() as conn:
        assert allow_login_attempt(
            conn, scope="login-account", subject="mysql-capacity-test", limit=2,
            window_seconds=60, now=181,
        )


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_CAPACITY") != "1" or DB_IS_SQLITE,
    reason="requires an explicitly selected disposable MySQL database",
)
def test_mysql_public_transfer_has_one_winner():
    if not settings.db_name.startswith("club_capacity_test_"):
        pytest.fail("refusing to run against a non-disposable MySQL database")

    run_id = uuid4().hex[:8]
    names = [f"transfer-{run_id}-{index}" for index in range(3)]
    tokens = [f"transfer-token-{run_id}-{index}" for index in range(3)]
    with tx() as conn:
        user_ids = []
        for name, token in zip(names, tokens):
            exec_one(conn, "insert into users(username, password, state) values (:name, 'test-only', 2)", {"name": name})
            user = fetch_one(conn, "select ID from users where username=:name", {"name": name})
            user_ids.append(user["id"])
            exec_one(
                conn, "insert into tokens(user_id, token, out_time) values (:uid, :token, :expiry)",
                {"uid": user["id"], "token": token, "expiry": datetime.now() + timedelta(hours=1)},
            )
        exec_one(conn, "insert into actions(title, state, max_num) values (:title, 3, 1)", {"title": names[0]})
        action = fetch_one(conn, "select ID from actions where title=:title", {"title": names[0]})
        exec_one(
            conn, "insert into records(user_id, action_id, sign_code, state) values (:uid, :aid, :code, 0)",
            {"uid": user_ids[0], "aid": action["id"], "code": f"transfer-old-{run_id}"},
        )
        record = fetch_one(conn, "select ID from records where action_id=:aid", {"aid": action["id"]})
        exec_one(
            conn, "insert into transfer(record_id, send_user_id, receive_user_id) values (:rid, :uid, :uid)",
            {"rid": record["id"], "uid": user_ids[0]},
        )
        transfer = fetch_one(conn, "select ID from transfer where record_id=:rid", {"rid": record["id"]})

    barrier = Barrier(2)

    def claim(token):
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                f"/api/transfer/acceptTransfer?transfer_id={transfer['id']}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            return token, response.json()["status"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(claim, tokens[1:]))
    assert sorted(status for _, status in outcomes) == [-1, 2]
    winner = next(token for token, status in outcomes if status == 2)
    with tx() as conn:
        owner = fetch_one(
            conn, "select r.user_id from records r where r.ID=:rid", {"rid": record["id"]},
        )
        assert owner["user_id"] == user_ids[tokens.index(winner)]
        assert fetch_one(conn, "select count(*) as c from transfer where ID=:id", {"id": transfer["id"]})["c"] == 0
