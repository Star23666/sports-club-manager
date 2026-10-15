from contextlib import contextmanager

from app.api import user as user_api


class DummyConn:
    pass


@contextmanager
def _fake_tx():
    yield DummyConn()


def test_user_login_not_found(client, monkeypatch):
    monkeypatch.setattr(user_api, "tx", _fake_tx)
    monkeypatch.setattr(user_api, "fetch_one", lambda *_args, **_kwargs: None)

    r = client.post("/api/user/login", params={"username": "u1"}, json={"password": "p1"})
    assert r.status_code == 200
    assert r.json() == {"status": -2, "data": None}


def test_user_login_success(client, monkeypatch):
    monkeypatch.setattr(user_api, "tx", _fake_tx)

    def fake_fetch_one(_conn, sql, _params=None):
        if "from users" in sql:
            return {"id": 1, "password": "ENC", "state": 2}
        return None

    called = {"exec": 0}

    monkeypatch.setattr(user_api, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(user_api, "exec_one", lambda *_args, **_kwargs: called.__setitem__("exec", called["exec"] + 1) or 1)
    monkeypatch.setattr(user_api, "verify_user_password", lambda *_args: True)
    monkeypatch.setattr(user_api, "new_token", lambda: "tok-user")

    r = client.post("/api/user/login", params={"username": "u1"}, json={"password": "p1"})
    assert r.status_code == 200
    assert r.json() == {"status": 2, "data": "tok-user"}
    assert called["exec"] == 2


def test_user_verify_uses_token_verify(client, monkeypatch):
    monkeypatch.setattr(user_api, "tx", _fake_tx)
    monkeypatch.setattr(user_api, "token_verify_member", lambda *_args, **_kwargs: (1, {"id": 5}))

    r = client.post("/api/user/verify", headers={"Authorization": "Bearer abc"})
    assert r.status_code == 200
    assert r.json() == {"status": 1, "data": {"id": 5}}


def test_change_password_invalid_format(client):
    r = client.post(
        "/api/user/password",
        headers={"Authorization": "Bearer t"},
        json={"origin_pass": "old", "new_pass": "short"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == -2


def test_logout_token_not_found(client, monkeypatch):
    monkeypatch.setattr(user_api, "tx", _fake_tx)
    monkeypatch.setattr(user_api, "fetch_one", lambda *_args, **_kwargs: {"c": 0})

    r = client.post("/api/user/logout", headers={"Authorization": "Bearer none"})
    assert r.status_code == 200
    assert r.json() == -1


def test_register_invalid_password(client):
    r = client.post(
        "/api/user/register",
        params={
            "username": "u1",
            "name": "n",
            "card_id": "c",
            "phone": "p",
            "wechat_id": "w",
            "student_id": "s",
            "email": "a@b.com",
        },
        json={"password": "weak"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == -1
