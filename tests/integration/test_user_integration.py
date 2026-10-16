from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine

from app import db as db_module
from app import main as app_main
from app.utils import encrypt_md5
from app.passwords import LEGACY_DEFAULT_ADMIN_HASH
from app.api import find as find_api
from app import rate_limit as rate_limit_module
from app.settings import settings
from app.passwords import hash_password


@pytest.fixture
def integration_client(tmp_path, monkeypatch):
    db_file = tmp_path / "integration.sqlite3"
    engine = create_engine(f"sqlite:///{db_file}")

    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                name TEXT,
                card_id TEXT,
                phone TEXT,
                state INTEGER,
                wechat_id TEXT,
                student_id TEXT,
                email TEXT
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                out_time TEXT
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                equip_id TEXT,
                user_id INTEGER
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE verifycode (
                user_id INTEGER PRIMARY KEY,
                code TEXT,
                out_time TEXT
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE recovery_rate_limit (
                bucket_key TEXT PRIMARY KEY,
                window_start INTEGER NOT NULL,
                hits INTEGER NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE login_rate_limit (
                bucket_key TEXT PRIMARY KEY,
                window_start INTEGER NOT NULL,
                hits INTEGER NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE user_view (
                ID INTEGER PRIMARY KEY,
                username TEXT,
                state INTEGER,
                phone TEXT,
                email TEXT,
                wechat_id TEXT,
                student_id TEXT,
                name TEXT
            )
            """
        )

    monkeypatch.setattr(db_module, "engine", engine)

    from fastapi.testclient import TestClient

    return TestClient(app_main.app)


def test_register_duplicate_then_reject(integration_client):
    params = {
        "username": "u100",
        "password": "Aa1$aaaa",
        "name": "N",
        "card_id": "C",
        "phone": "P",
        "wechat_id": "W",
        "student_id": "S",
        "email": "u100@example.com",
    }

    r1 = integration_client.post("/api/user/register", json=params)
    assert r1.status_code == 200
    assert r1.json()["status"] == 0
    with db_module.engine.begin() as conn:
        stored = conn.exec_driver_sql("select password from users where username='u100'").scalar_one()
    assert stored.startswith("$argon2id$")

    r2 = integration_client.post("/api/user/register", json=params)
    assert r2.status_code == 200
    assert r2.json()["status"] == -1


def test_member_and_admin_share_login_attempt_limit(integration_client, monkeypatch):
    monkeypatch.setattr(settings, "login_account_limit", 2)
    monkeypatch.setattr(settings, "login_ip_limit", 20)
    monkeypatch.setattr(settings, "login_window_seconds", 900)
    now = [1800]
    monkeypatch.setattr(rate_limit_module.time, "time", lambda: now[0])
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("limit-member", hash_password("Aa1$abcd"), 2),
        )

    wrong = {"username": "limit-member", "password": "wrong"}
    assert integration_client.post("/api/user/login", json=wrong).json()["status"] == -2
    assert integration_client.post("/admin/api/user/login", json=wrong).json()["status"] == -2
    assert integration_client.post("/api/user/login", json=wrong).json()["status"] == -3
    # A correct password cannot bypass an active account window.
    assert integration_client.post(
        "/api/user/login", json={"username": "limit-member", "password": "Aa1$abcd"}
    ).json()["status"] == -3

    now[0] += 901
    assert integration_client.post(
        "/api/user/login", json={"username": "limit-member", "password": "Aa1$abcd"}
    ).json()["status"] == 2
    with db_module.engine.begin() as conn:
        assert conn.exec_driver_sql("select count(*) from login_rate_limit").scalar_one() == 1


def test_login_ip_limit_ignores_untrusted_forwarded_header(integration_client, monkeypatch):
    monkeypatch.setattr(settings, "login_account_limit", 20)
    monkeypatch.setattr(settings, "login_ip_limit", 2)
    monkeypatch.setattr(settings, "login_window_seconds", 900)
    for index in range(2):
        response = integration_client.post(
            "/api/user/login",
            json={"username": f"missing-{index}", "password": "wrong"},
            headers={"X-Forwarded-For": f"203.0.113.{index + 1}"},
        )
        assert response.json()["status"] == -2
    blocked = integration_client.post(
        "/admin/api/user/login",
        json={"username": "another-missing", "password": "wrong"},
        headers={"X-Forwarded-For": "203.0.113.99"},
    )
    assert blocked.json()["status"] == -3


def test_verify_with_valid_token(integration_client):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("member01", encrypt_md5("Aa1$aaaa"), 2),
        )
        user_id = conn.exec_driver_sql("select id from users where username=?", ("member01",)).scalar_one()

        conn.exec_driver_sql(
            "insert into user_view(ID, username, state, phone, email, wechat_id, student_id, name)"
            " values (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, "member01", 2, "138", "m@example.com", "wx", "sid", "Member"),
        )
        conn.exec_driver_sql(
            "insert into tokens(user_id, token, out_time) values (?, ?, ?)",
            (user_id, "tok-ok", (datetime.now() + timedelta(hours=1)).isoformat()),
        )

    r = integration_client.post("/api/user/verify", headers={"Authorization": "Bearer tok-ok"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert body["data"]["username"] == "member01"


def test_legacy_member_login_upgrades_password(integration_client):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("old-member", encrypt_md5("Aa1$oldpass"), 2),
        )

    response = integration_client.post(
        "/api/user/login", json={"username": "old-member", "password": "Aa1$oldpass"}
    )
    assert response.json()["status"] == 2
    assert response.json()["data"]
    with db_module.engine.begin() as conn:
        stored = conn.exec_driver_sql("select password from users where username='old-member'").scalar_one()
        assert stored.startswith("$argon2id$")
        user_id = conn.exec_driver_sql("select id from users where username='old-member'").scalar_one()
        conn.exec_driver_sql(
            "insert into user_view(ID, username, state) values (?, ?, ?)",
            (user_id, "old-member", 2),
        )
    verified = integration_client.post(
        "/api/user/verify", headers={"Authorization": f"Bearer {response.json()['data']}"}
    )
    assert verified.json()["status"] == 1


def test_public_legacy_admin_password_is_rejected(integration_client):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("admin", LEGACY_DEFAULT_ADMIN_HASH, 4),
        )

    response = integration_client.post(
        "/admin/api/user/login", json={"username": "admin", "password": "admin"}
    )
    assert response.json()["status"] == -2


def test_logout_removes_token(integration_client):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("logout-user", encrypt_md5("Aa1$aaaa"), 2),
        )
        user_id = conn.exec_driver_sql("select id from users where username=?", ("logout-user",)).scalar_one()
        conn.exec_driver_sql(
            "insert into tokens(user_id, token, out_time) values (?, ?, ?)",
            (user_id, "tok-logout", (datetime.now() + timedelta(hours=1)).isoformat()),
        )

    r = integration_client.post("/api/user/logout", headers={"Authorization": "Bearer tok-logout"})
    assert r.status_code == 200
    assert r.json() == 0

    with db_module.engine.begin() as conn:
        remaining = conn.exec_driver_sql("select count(*) from tokens where token=?", ("tok-logout",)).scalar_one()
    assert remaining == 0


@pytest.mark.parametrize(
    ("state", "path", "expected_status"),
    [
        (2, "/admin/api/member/queryMembers", -1),
        (4, "/api/action/queryRecord", 0),
    ],
)
def test_role_tokens_cannot_cross_member_admin_boundary(integration_client, state, path, expected_status):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            (f"role-{state}", encrypt_md5("Aa1$aaaa"), state),
        )
        user_id = conn.exec_driver_sql("select id from users where username=?", (f"role-{state}",)).scalar_one()
        conn.exec_driver_sql(
            "insert into user_view(ID, username, state) values (?, ?, ?)",
            (user_id, f"role-{state}", state),
        )
        conn.exec_driver_sql(
            "insert into tokens(user_id, token, out_time) values (?, ?, ?)",
            (user_id, f"role-token-{state}", (datetime.now() + timedelta(hours=1)).isoformat()),
        )

    response = integration_client.post(path, headers={"Authorization": f"Bearer role-token-{state}"})
    assert response.json()["status"] == expected_status


def test_existing_device_fingerprint_cannot_issue_token_or_enroll_new_device(integration_client):
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, state) values (?, ?, ?)",
            ("device-owner", encrypt_md5("Aa1$aaaa"), 2),
        )
        user_id = conn.exec_driver_sql("select id from users where username='device-owner'").scalar_one()
        conn.exec_driver_sql(
            "insert into equipment(name, equip_id, user_id) values (?, ?, ?)",
            ("old-device", encrypt_md5("known-fingerprint"), user_id),
        )
        conn.exec_driver_sql(
            "insert into tokens(user_id, token, out_time) values (?, ?, ?)",
            (user_id, "member-token", None),
        )

    login = integration_client.post("/api/user/loginByEquip", params={"equip_id": "known-fingerprint"})
    assert login.json()["status"] < 0
    enroll = integration_client.post(
        "/api/user/newEquipment",
        headers={"Authorization": "Bearer member-token"},
        json={"equip_id": "new-fingerprint", "name": "new-device", "password": "Aa1$aaaa"},
    )
    assert enroll.json()["status"] < 0
    with db_module.engine.begin() as conn:
        assert conn.exec_driver_sql("select count(*) from tokens").scalar_one() == 1
        assert conn.exec_driver_sql("select count(*) from equipment").scalar_one() == 1


def test_recovery_lookup_limits_same_identity_and_ignores_spoofed_forwarded_ip(integration_client):
    for attempt in range(4):
        response = integration_client.post(
            "/api/find/queryUserName",
            json={"name": "Unknown", "student_id": "not-found"},
            headers={"X-Forwarded-For": f"192.0.2.{attempt + 1}"},
        )
        assert response.json()["status"] == (-3 if attempt == 3 else -1)


def test_recovery_lookup_limits_ip_even_with_distinct_identities(integration_client):
    for attempt in range(13):
        response = integration_client.post(
            "/api/find/queryUserName", json={"name": f"Unknown-{attempt}", "student_id": "not-found"}
        )
        assert response.json()["status"] == (-3 if attempt == 12 else -1)


def test_reset_code_guessing_is_limited(integration_client):
    for attempt in range(11):
        response = integration_client.post(
            "/api/find/resetPassword", json={"code": f"wrong-{attempt}", "password": "Aa1$aaaa"}
        )
        assert response.json()["status"] == (-3 if attempt == 10 else -2)


def test_reset_email_throttle_and_valid_code_work_with_sqlite_dates(integration_client, monkeypatch):
    monkeypatch.setattr(find_api, "send_reset_email", lambda *_args: True)
    with db_module.engine.begin() as conn:
        conn.exec_driver_sql(
            "insert into users(username, password, name, student_id, email, state) values (?, ?, ?, ?, ?, ?)",
            ("recover-me", encrypt_md5("Aa1$oldpass"), "Member", "S100", "member@example.com", 2),
        )

    payload = {"username": "recover-me", "name": "Member", "student_id": "S100"}
    first = integration_client.post("/api/find/sendResetEmail", json=payload)
    assert first.json()["status"] == 1
    second = integration_client.post("/api/find/sendResetEmail", json=payload)
    assert second.json()["status"] == -1
    third = integration_client.post("/api/find/sendResetEmail", json=payload)
    assert third.json()["status"] == -3

    with db_module.engine.begin() as conn:
        code = conn.exec_driver_sql("select code from verifycode").scalar_one()
    reset = integration_client.post("/api/find/resetPassword", json={"code": code, "password": "Aa1$newpass"})
    assert reset.json()["status"] == 0
    login = integration_client.post(
        "/api/user/login", json={"username": "recover-me", "password": "Aa1$newpass"}
    )
    assert login.json()["status"] == 2
