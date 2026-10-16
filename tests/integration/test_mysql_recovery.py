"""Optional MySQL migration smoke test.

Run only against a disposable ``club_upgrade_test*`` database with
``DB_TYPE=mysql`` and ``TEST_MYSQL_MIGRATION=1`` after applying the migration.
"""

import os
import uuid

import pytest
from sqlalchemy import text

from app.db import DB_IS_SQLITE, tx
from app.rate_limit import allow_recovery_attempt
from app.settings import settings


@pytest.mark.skipif(
    os.getenv("TEST_MYSQL_MIGRATION") != "1" or DB_IS_SQLITE,
    reason="requires an explicit disposable MySQL test database",
)
def test_migrated_mysql_rate_limit_respects_windows_and_keeps_legacy_user():
    if not settings.db_name.startswith("club_upgrade_test"):
        pytest.fail("refusing to test against a non-disposable MySQL database")

    subject = f"smoke-{uuid.uuid4()}"
    with tx() as conn:
        columns = conn.execute(
            text(
                "select CHARACTER_MAXIMUM_LENGTH from information_schema.COLUMNS "
                "where TABLE_SCHEMA=:schema and TABLE_NAME='users' and COLUMN_NAME='password'"
            ),
            {"schema": settings.db_name},
        ).scalar_one()
        assert columns == 255
        assert conn.execute(text("select password from users where username='legacy-member'")).scalar_one() == "a" * 32

        assert allow_recovery_attempt(conn, scope="mysql-smoke", subject=subject, limit=2, window_seconds=60, now=120)
        assert allow_recovery_attempt(conn, scope="mysql-smoke", subject=subject, limit=2, window_seconds=60, now=121)
        assert not allow_recovery_attempt(conn, scope="mysql-smoke", subject=subject, limit=2, window_seconds=60, now=122)
        assert allow_recovery_attempt(conn, scope="mysql-smoke", subject=subject, limit=2, window_seconds=60, now=180)
