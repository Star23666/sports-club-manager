from contextlib import contextmanager

import pytest

from app.api import transfer


@contextmanager
def _fake_tx():
    yield object()


@pytest.mark.parametrize(
    ("action_state", "record_state", "record_owner"),
    [(4, 0, 7), (3, 1, 7), (3, 0, 9)],
)
def test_stale_transfer_cannot_change_booking(client, monkeypatch, action_state, record_state, record_owner):
    monkeypatch.setattr(transfer, "tx", lambda **_kwargs: _fake_tx())
    monkeypatch.setattr(transfer, "token_verify_member", lambda *_: (1, {"id": 8, "state": 2}))
    rows = iter(
        [
            {"record_id": 20},
            {"action_id": 30},
            {"id": 10, "record_id": 20, "send_user_id": 7, "receive_user_id": 8},
            {"id": 20, "action_id": 30, "user_id": record_owner, "state": record_state},
        ]
    )
    monkeypatch.setattr(transfer, "fetch_one", lambda *_args, **_kwargs: next(rows))
    monkeypatch.setattr(transfer, "lock_action", lambda *_args: {"id": 30, "state": action_state})
    monkeypatch.setattr(
        transfer,
        "exec_one",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("stale transfer wrote data")),
    )

    response = client.post("/api/transfer/acceptTransfer?transfer_id=10", headers={"Authorization": "Bearer test"})
    assert response.json()["status"] == 0
