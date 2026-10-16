from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager, suppress

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from .settings import settings


def _build_engine() -> Engine:
    """Create engine with dialect-appropriate options."""
    if settings.is_sqlite:
        return create_engine(
            settings.sqlalchemy_url,
            connect_args={"check_same_thread": False},
        )
    return create_engine(
        settings.sqlalchemy_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine: Engine = _build_engine()

# Dialect flag for SQL compatibility helpers.
DB_IS_SQLITE: bool = settings.is_sqlite


def sql_binary(col: str) -> str:
    """Return SQL fragment for case-sensitive comparison.

    MySQL utf8mb4_0900_ai_ci is case-insensitive → wrap with BINARY.
    SQLite TEXT is natively case-sensitive → no wrapping needed.
    """
    if DB_IS_SQLITE:
        return col
    return f"BINARY {col}"


def _init_sqlite_schema() -> None:
    """Create tables, views, and seed data on first SQLite startup."""
    from .db_schema import SCHEMA_DDL

    with engine.begin() as conn:
        for statement in SCHEMA_DDL:
            with suppress(Exception):
                conn.execute(text(statement))


if settings.is_sqlite:
    _init_sqlite_schema()


@contextmanager
def tx(*, immediate: bool = False) -> Iterator[Connection]:
    with engine.begin() as conn:
        # SQLite has no row-level SELECT FOR UPDATE. Reserve its single writer
        # before reading the capacity, rather than trying to upgrade a stale
        # read transaction after another request has enrolled.
        if immediate and DB_IS_SQLITE:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
        yield conn


def lock_action(conn: Connection, action_id: int) -> dict | None:
    """Serialize capacity decisions for one action within the caller's tx."""
    suffix = "" if DB_IS_SQLITE else " for update"
    return fetch_one(conn, f"select * from actions where ID=:id{suffix}", {"id": action_id})


def fetch_one(conn: Connection, sql: str, params: dict | None = None, *, for_update: bool = False) -> dict | None:
    if for_update and not DB_IS_SQLITE:
        sql += " for update"
    row = conn.execute(text(sql), params or {}).mappings().first()
    return normalize_row(row) if row else None


def fetch_all(conn: Connection, sql: str, params: dict | None = None, *, for_update: bool = False) -> list[dict]:
    if for_update and not DB_IS_SQLITE:
        sql += " for update"
    rows = conn.execute(text(sql), params or {}).mappings().all()
    return [normalize_row(r) for r in rows]


def exec_one(conn: Connection, sql: str, params: dict | None = None) -> int:
    result = conn.execute(text(sql), params or {})
    return int(result.rowcount or 0)


def normalize_row(row: dict) -> dict:
    # MySQL columns often come as `ID`; Java entities use `id`.
    out: dict = {}
    for k, v in row.items():
        key = "id" if k == "ID" else k
        out[key] = v
    return out
