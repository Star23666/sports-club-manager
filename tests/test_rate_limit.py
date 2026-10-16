from sqlalchemy import create_engine

from app.rate_limit import allow_recovery_attempt


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
