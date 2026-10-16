from contextlib import contextmanager

import pytest

from app.main import app
from app.api import action, transfer, waiting


PUBLIC_ROUTES = {
    "/api/user/login",
    "/api/user/register",
    "/api/user/loginByEquip",  # permanently rejects device-only login
    "/api/user/newEquipment",  # permanently rejects device enrollment
    "/admin/api/user/login",
    "/api/find/queryUserName",
    "/api/find/sendResetEmail",
    "/api/find/resetPassword",
}


def test_every_other_api_route_requires_authorization_header():
    for path, operations in app.openapi()["paths"].items():
        if path in PUBLIC_ROUTES:
            continue
        parameters = operations["post"].get("parameters", [])
        assert any(p["in"] == "header" and p["name"] == "authorization" for p in parameters), path


@contextmanager
def _fake_tx(**_kwargs):
    yield object()


@pytest.mark.parametrize(
    ("module", "path", "params", "rows", "denied_status"),
    [
        (
            action,
            "/api/action/cancelAction",
            {"record_id": 10},
            [{"id": 10, "user_id": 99, "action_id": 20}, {"id": 20, "state": 2}],
            1,
        ),
        (
            action,
            "/api/action/queryWechatGroup",
            {"record_id": 10},
            [{"id": 10, "user_id": 99, "action_id": 20}],
            0,
        ),
        (
            waiting,
            "/api/waiting/waitDelete",
            {"waiting_id": 10},
            [{"id": 10, "user_id": 99, "action_id": 20}],
            0,
        ),
        (
            transfer,
            "/api/transfer/transferRecord",
            {"record_id": 10},
            [{"id": 10, "user_id": 99, "action_id": 20}, {"id": 20, "state": 3}],
            1,
        ),
        (
            transfer,
            "/api/transfer/acceptTransfer",
            {"transfer_id": 10},
            [{"id": 10, "receive_user_id": 99, "send_user_id": 88}],
            0,
        ),
        (
            transfer,
            "/api/transfer/refuseTransfer",
            {"transfer_id": 10},
            [{"id": 10, "receive_user_id": 99, "send_user_id": 88}],
            0,
        ),
    ],
)
def test_member_cannot_read_or_mutate_another_members_resources(
    client, monkeypatch, module, path, params, rows, denied_status
):
    monkeypatch.setattr(module, "tx", _fake_tx)
    monkeypatch.setattr(module, "token_verify_member", lambda *_: (1, {"id": 7, "state": 2}))
    if path in {"/api/action/cancelAction", "/api/waiting/waitDelete"}:
        monkeypatch.setattr(module, "lock_action", lambda *_args: {"id": 20, "state": 2})
        row_iter = iter([rows[0], rows[0]])
    else:
        row_iter = iter(rows)
    monkeypatch.setattr(module, "fetch_one", lambda *_args, **_kwargs: next(row_iter))
    monkeypatch.setattr(
        module, "exec_one", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unauthorized write"))
    )

    response = client.post(path, params=params, headers={"Authorization": "Bearer member"}, json={"receive_user": ""})
    assert response.json()["status"] == denied_status
