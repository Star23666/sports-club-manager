"""Database-backed, fixed-window limits for account recovery requests.

The database upsert is atomic, so counters are shared across API workers.
Only a SHA-256 digest of the bucket subject is stored, never the raw IP or ID.
"""

from __future__ import annotations

import hashlib
import time

from sqlalchemy.engine import Connection

from .db import DB_IS_SQLITE, exec_one, fetch_one


def allow_recovery_attempt(
    conn: Connection,
    *,
    scope: str,
    subject: str,
    limit: int,
    window_seconds: int,
    now: int | None = None,
) -> bool:
    """Count the attempt and return whether it is within the allowed window."""
    if limit < 1 or window_seconds < 1:
        raise ValueError("rate-limit settings must be positive")

    timestamp = int(time.time()) if now is None else now
    window_start = timestamp - timestamp % window_seconds
    bucket_key = hashlib.sha256(f"{scope}\0{subject}".encode("utf-8")).hexdigest()
    params = {"key": bucket_key, "window": window_start}

    if DB_IS_SQLITE:
        exec_one(
            conn,
            "insert into recovery_rate_limit(bucket_key, window_start, hits) values (:key, :window, 1) "
            "on conflict(bucket_key) do update set "
            "hits = case when recovery_rate_limit.window_start = excluded.window_start "
            "then recovery_rate_limit.hits + 1 else 1 end, "
            "window_start = excluded.window_start",
            params,
        )
    else:
        exec_one(
            conn,
            "insert into recovery_rate_limit(bucket_key, window_start, hits) values (:key, :window, 1) "
            "on duplicate key update "
            "hits = if(window_start = values(window_start), hits + 1, 1), "
            "window_start = values(window_start)",
            params,
        )

    row = fetch_one(conn, "select hits from recovery_rate_limit where bucket_key=:key", {"key": bucket_key})
    exec_one(
        conn,
        "delete from recovery_rate_limit where window_start < :cutoff",
        {"cutoff": timestamp - 86400},
    )
    # Fail closed if the row cannot be read. An SQL exception also aborts the request.
    return bool(row and int(row["hits"]) <= limit)


def recovery_client_ip(request) -> str:
    """Use the direct peer, never an untrusted X-Forwarded-For header."""
    return request.client.host if request.client else "unknown"
