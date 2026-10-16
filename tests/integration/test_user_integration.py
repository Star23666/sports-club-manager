from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine

from app import db as db_module
from app import main as app_main
from app.utils import encrypt_md5
from app.passwords import LEGACY_DEFAULT_ADMIN_HASH


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
            (user_id, "tok-ok", None),
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
            (user_id, f"role-token-{state}", None),
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
