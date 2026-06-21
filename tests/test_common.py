from datetime import datetime, timedelta

import pytest

from app.api import common


class DummyConn:
    pass


def test_token_verify_member_empty_token():
    status, user = common.token_verify_member(DummyConn(), "")
    assert status == -1
    assert user is None


def test_token_verify_member_expired_token_deletes(monkeypatch):
    calls = {"exec": 0}

    def fake_fetch_one(_conn, sql, _params=None):
        if "count(*) as c from tokens" in sql:
            return {"c": 1}
        if "select * from tokens" in sql:
            return {"user_id": 1, "out_time": datetime.now() - timedelta(seconds=1)}
        pytest.fail(f"unexpected sql: {sql}")

    def fake_exec_one(_conn, sql, _params=None):
        if "delete from tokens" in sql:
            calls["exec"] += 1
        return 1

    monkeypatch.setattr(common, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(common, "exec_one", fake_exec_one)

    status, user = common.token_verify_member(DummyConn(), "t1")
    assert status == 0
    assert user is None
    assert calls["exec"] == 1


def test_token_verify_member_success(monkeypatch):
    user_view = {"id": 7, "state": 2}

    def fake_fetch_one(_conn, sql, _params=None):
        if "count(*) as c from tokens" in sql:
            return {"c": 1}
        if "select * from tokens" in sql:
            return {"user_id": 7, "out_time": datetime.now() + timedelta(hours=1)}
        if "select * from user_view" in sql:
            return user_view
        pytest.fail(f"unexpected sql: {sql}")

    monkeypatch.setattr(common, "fetch_one", fake_fetch_one)

    status, user = common.token_verify_member(DummyConn(), "t2")
    assert status == 1
    assert user == user_view


def test_login_common_admin_success(monkeypatch):
    calls = {"exec": 0}

    def fake_fetch_one(_conn, sql, _params=None):
        if "from users" in sql:
            return {"id": 9, "password": "ENC", "state": 4}
        pytest.fail(f"unexpected sql: {sql}")

    def fake_exec_one(_conn, _sql, _params=None):
        calls["exec"] += 1
        return 1

    monkeypatch.setattr(common, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(common, "exec_one", fake_exec_one)
    monkeypatch.setattr(common, "encrypt_md5", lambda _s: "ENC")
    monkeypatch.setattr(common, "new_token", lambda: "tok-admin")

    status, token = common.login_common(DummyConn(), "admin", "pwd", admin=True)
    assert status == 0
    assert token == "tok-admin"
    assert calls["exec"] == 2


def test_login_common_member_wrong_password(monkeypatch):
    monkeypatch.setattr(common, "fetch_one", lambda *_args, **_kwargs: {"id": 1, "password": "A", "state": 1})
    monkeypatch.setattr(common, "encrypt_md5", lambda _s: "B")

    status, token = common.login_common(DummyConn(), "u", "bad", admin=False)
    assert status == -2
    assert token is None
