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
def tx() -> Iterator[Connection]:
    with engine.begin() as conn:
        yield conn


def fetch_one(conn: Connection, sql: str, params: dict | None = None) -> dict | None:
    row = conn.execute(text(sql), params or {}).mappings().first()
    return normalize_row(row) if row else None


def fetch_all(conn: Connection, sql: str, params: dict | None = None) -> list[dict]:
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
