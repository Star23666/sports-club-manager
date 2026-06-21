import json

from app.response import vo, vo_json


def test_vo_returns_stable_shape():
    assert vo(1, {"k": "v"}) == {"status": 1, "data": {"k": "v"}}


def test_vo_json_returns_json_response():
    resp = vo_json(2, [1, 2, 3])
    payload = json.loads(resp.body.decode("utf-8"))
    assert payload == {"status": 2, "data": [1, 2, 3]}
