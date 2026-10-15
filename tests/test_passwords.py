from sqlalchemy import create_engine

from app.bootstrap_admin import create_or_rotate_admin
from app.passwords import LEGACY_DEFAULT_ADMIN_HASH, hash_password, verify_user_password
from app.utils import encrypt_md5


def _database():
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create table users (id integer primary key, username text unique, password text, name text, state integer)"
        )
        conn.exec_driver_sql("create table tokens (user_id integer, token text)")
    return engine


def test_new_password_is_argon2_and_rejects_wrong_password():
    engine = _database()
    with engine.begin() as conn:
        password_hash = hash_password("Aa1$long-secret")
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("member", password_hash, 2),
        )
        user = conn.exec_driver_sql("select * from users").mappings().one()
        assert password_hash.startswith("$argon2id$")
        assert verify_user_password(conn, user, "Aa1$long-secret")
        assert not verify_user_password(conn, user, "wrong")


def test_legacy_password_upgrades_after_correct_login():
    engine = _database()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("member", encrypt_md5("Aa1$legacy"), 2),
        )
        user = dict(conn.exec_driver_sql("select * from users").mappings().one())
        assert not verify_user_password(conn, user, "bad")
        assert verify_user_password(conn, user, "Aa1$legacy")
        upgraded = dict(conn.exec_driver_sql("select * from users").mappings().one())
        assert upgraded["password"].startswith("$argon2id$")
        assert verify_user_password(conn, upgraded, "Aa1$legacy")


def test_public_default_admin_cannot_login_until_rotated():
    engine = _database()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("admin", LEGACY_DEFAULT_ADMIN_HASH, 4),
        )
        user = dict(conn.exec_driver_sql("select * from users").mappings().one())
        assert not verify_user_password(conn, user, "admin")
        assert create_or_rotate_admin(conn, "owner", "Aa1$uniqueLong") == "rotated"
        rotated = dict(conn.exec_driver_sql("select * from users").mappings().one())
        assert rotated["username"] == "owner"
        assert verify_user_password(conn, rotated, "Aa1$uniqueLong")


def test_bootstrap_creates_only_one_administrator():
    engine = _database()
    with engine.begin() as conn:
        assert create_or_rotate_admin(conn, "owner", "Aa1$uniqueLong") == "created"
        assert conn.exec_driver_sql("select count(*) from users where state>=4").scalar_one() == 1
        try:
            create_or_rotate_admin(conn, "another", "Aa1$anotherLong")
        except ValueError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("second administrator must be rejected")
