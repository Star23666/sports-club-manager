from contextlib import contextmanager

from app.api import staff as staff_api


@contextmanager
def _fake_tx():
    yield object()


def test_only_assigned_staff_can_list_members(client, monkeypatch):
    monkeypatch.setattr(staff_api, "tx", _fake_tx)
    monkeypatch.setattr(staff_api, "token_verify_member", lambda *_: (1, {"id": 7, "state": 3}))
    monkeypatch.setattr(staff_api, "fetch_one", lambda *_args, **_kwargs: {"id": 12, "staff_user_id": 8})
    monkeypatch.setattr(staff_api, "fetch_all", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("member data leaked")))

    response = client.post("/api/staff/queryActionMember", params={"action_id": 12}, headers={"Authorization": "Bearer staff"})
    assert response.json()["status"] == 2
    assert response.json()["data"] == "Staff Not Match"


def test_assigned_staff_can_list_members(client, monkeypatch):
    monkeypatch.setattr(staff_api, "tx", _fake_tx)
    monkeypatch.setattr(staff_api, "token_verify_member", lambda *_: (1, {"id": 7, "state": 3}))
    monkeypatch.setattr(staff_api, "fetch_one", lambda *_args, **_kwargs: {"id": 12, "staff_user_id": 7})
    monkeypatch.setattr(staff_api, "fetch_all", lambda *_args, **_kwargs: [{"name": "Member"}])

    response = client.post("/api/staff/queryActionMember", params={"action_id": 12}, headers={"Authorization": "Bearer staff"})
    assert response.json() == {"status": 1, "data": [{"name": "Member"}]}


def test_wrong_staff_cannot_read_qr_member_or_complete_sign(client, monkeypatch):
    monkeypatch.setattr(staff_api, "tx", _fake_tx)
    monkeypatch.setattr(staff_api, "token_verify_member", lambda *_: (1, {"id": 7, "state": 3}))

    def fake_fetch_one(_conn, sql, _params):
        if "from records" in sql:
            return {"id": 20, "action_id": 12, "user_id": 2, "state": 0}
        if "from actions" in sql:
            return {"id": 12, "staff_user_id": 8, "state": 4}
        raise AssertionError("member data leaked")

    monkeypatch.setattr(staff_api, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(staff_api, "exec_one", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("record changed")))
    headers = {"Authorization": "Bearer staff"}
    query = client.post("/api/staff/querySign", headers=headers, json={"sign_code": "code"})
    assert query.json()["status"] == 2
    assert "mem_inf" not in str(query.json())

    finish = client.post("/api/staff/finishSign", headers=headers, json={"sign_code": "code"})
    assert finish.json()["status"] == 2


def test_member_cannot_use_staff_qr_endpoint(client, monkeypatch):
    monkeypatch.setattr(staff_api, "tx", _fake_tx)
    monkeypatch.setattr(staff_api, "token_verify_member", lambda *_: (1, {"id": 2, "state": 2}))
    monkeypatch.setattr(staff_api, "fetch_one", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("record accessed")))

    response = client.post(
        "/api/staff/querySign", headers={"Authorization": "Bearer member"}, json={"sign_code": "code"}
    )
    assert response.json()["status"] == -1
