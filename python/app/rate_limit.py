"""Database-backed, fixed-window limits for recovery, login, and registration.

The database upsert is atomic, so counters are shared across API workers.
Only a SHA-256 digest of the bucket subject is stored, never the raw IP or ID.
"""

from __future__ import annotations

import hashlib
import time
from ipaddress import ip_address

from sqlalchemy.engine import Connection

from .db import DB_IS_SQLITE, exec_one, fetch_one, tx
from .settings import settings


def _allow_attempt(
    conn: Connection,
    *,
    table: str,
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
            f"insert into {table}(bucket_key, window_start, hits) values (:key, :window, 1) "
            "on conflict(bucket_key) do update set "
            f"hits = case when {table}.window_start = excluded.window_start "
            f"then {table}.hits + 1 else 1 end, "
            "window_start = excluded.window_start",
            params,
        )
    else:
        exec_one(
            conn,
            f"insert into {table}(bucket_key, window_start, hits) values (:key, :window, 1) "
            "on duplicate key update "
            "hits = if(window_start = values(window_start), hits + 1, 1), "
            "window_start = values(window_start)",
            params,
        )

    row = fetch_one(conn, f"select hits from {table} where bucket_key=:key", {"key": bucket_key})
    exec_one(
        conn,
        f"delete from {table} where window_start < :cutoff",
        {"cutoff": timestamp - 86400},
    )
    # Fail closed if the row cannot be read. An SQL exception also aborts the request.
    return bool(row and int(row["hits"]) <= limit)


def allow_recovery_attempt(
    conn: Connection, *, scope: str, subject: str, limit: int, window_seconds: int, now: int | None = None
) -> bool:
    return _allow_attempt(
        conn, table="recovery_rate_limit", scope=scope, subject=subject,
        limit=limit, window_seconds=window_seconds, now=now,
    )


def allow_login_attempt(
    conn: Connection, *, scope: str, subject: str, limit: int, window_seconds: int, now: int | None = None
) -> bool:
    """Reserve one attempt atomically before expensive password verification."""
    return _allow_attempt(
        conn, table="login_rate_limit", scope=scope, subject=subject,
        limit=limit, window_seconds=window_seconds, now=now,
    )


def clear_login_account_attempts(conn: Connection, username: str) -> None:
    """Successful authentication clears only this account's bucket, not its IP's."""
    key = hashlib.sha256(f"login-account\0{username.casefold()}".encode("utf-8")).hexdigest()
    exec_one(conn, "delete from login_rate_limit where bucket_key=:key", {"key": key})


def reserve_login_request(request, username: str) -> bool:
    """Share account and direct-peer limits across member and admin logins."""
    with tx() as conn:
        ip_allowed = allow_login_attempt(
            conn, scope="login-ip", subject=recovery_client_ip(request),
            limit=settings.login_ip_limit, window_seconds=settings.login_window_seconds,
        )
        account_allowed = allow_login_attempt(
            conn, scope="login-account", subject=username.casefold(),
            limit=settings.login_account_limit, window_seconds=settings.login_window_seconds,
        )
    return ip_allowed and account_allowed


def reserve_registration_request(request) -> bool:
    """Limit direct registration attempts before password hashing and user creation."""
    with tx() as conn:
        return allow_recovery_attempt(
            conn, scope="register:ip", subject=recovery_client_ip(request),
            limit=settings.register_ip_limit, window_seconds=settings.register_window_seconds,
        )


def recovery_client_ip(request) -> str:
    """Use a proxy-overwritten real IP only for an explicitly trusted peer."""
    peer = request.client.host if request.client else "unknown"
    try:
        peer_address = ip_address(peer)
    except ValueError:
        return peer

    if peer_address in settings.trusted_proxy_addresses:
        # Our bundled Nginx config overwrites this header with $remote_addr.
        # Duplicates or malformed values fall back to the peer's shared bucket.
        values = request.headers.getlist("x-real-ip")
        if len(values) == 1:
            try:
                return str(ip_address(values[0].strip()))
            except ValueError:
                pass
    return str(peer_address)
