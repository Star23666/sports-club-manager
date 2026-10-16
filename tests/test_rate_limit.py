from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import create_engine

from app.rate_limit import allow_login_attempt, allow_recovery_attempt, clear_login_account_attempts


def test_fixed_window_counter_shared_between_connections(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'limits.sqlite3'}")
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create table recovery_rate_limit (bucket_key text primary key, window_start integer not null, hits integer not null)"
        )

    results = []
    for attempt in range(4):
        with engine.begin() as conn:
            results.append(
                allow_recovery_attempt(
                    conn, scope="test", subject="person@example.com", limit=2, window_seconds=60, now=120 + attempt
                )
            )
    assert results == [True, True, False, False]

    with engine.begin() as conn:
        assert allow_recovery_attempt(
            conn, scope="test", subject="person@example.com", limit=2, window_seconds=60, now=180
        )
        stored = conn.exec_driver_sql("select bucket_key, hits from recovery_rate_limit").one()
    assert stored.hits == 1
    assert "person@example.com" not in stored.bucket_key


def test_login_counter_is_atomic_across_connections_and_success_clears_only_account(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login-limits.sqlite3'}")
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create table login_rate_limit (bucket_key text primary key, window_start integer not null, hits integer not null)"
        )

    results = []
    for attempt in range(4):
        with engine.begin() as conn:
            results.append(allow_login_attempt(
                conn, scope="login-account", subject="member", limit=2, window_seconds=60, now=120 + attempt,
            ))
    assert results == [True, True, False, False]

    with engine.begin() as conn:
        assert allow_login_attempt(conn, scope="login-ip", subject="127.0.0.1", limit=10, window_seconds=60, now=124)
        clear_login_account_attempts(conn, "MEMBER")
        rows = conn.exec_driver_sql("select bucket_key from login_rate_limit").all()
    assert len(rows) == 1  # the IP counter survives a successful account login
    assert "127.0.0.1" not in rows[0].bucket_key

    with engine.begin() as conn:
        assert allow_login_attempt(conn, scope="login-account", subject="member", limit=2, window_seconds=60, now=125)


def test_parallel_login_reservations_only_allow_the_limit(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'parallel-login.sqlite3'}", connect_args={"check_same_thread": False}
    )
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create table login_rate_limit (bucket_key text primary key, window_start integer not null, hits integer not null)"
        )
    barrier = Barrier(8)

    def attempt(_index):
        barrier.wait(timeout=10)
        with engine.begin() as conn:
            return allow_login_attempt(
                conn, scope="login-account", subject="same-member", limit=3,
                window_seconds=60, now=120,
            )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(8)))
    assert results.count(True) == 3
    assert results.count(False) == 5
