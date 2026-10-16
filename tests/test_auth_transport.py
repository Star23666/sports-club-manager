from app.main import app


def test_sensitive_credentials_are_not_query_parameters():
    for route in app.openapi()["paths"].values():
        for operation in route.values():
            if not isinstance(operation, dict):
                continue
            query_names = {
                parameter["name"]
                for parameter in operation.get("parameters", [])
                if parameter["in"] == "query"
            }
            assert not {"token", "password", "origin_pass", "new_pass", "code"} & query_names


def test_query_token_is_not_accepted(client):
    response = client.post("/api/user/verify", params={"token": "anything"})
    assert response.json()["status"] == -1


def test_query_password_is_not_accepted(client):
    response = client.post(
        "/api/user/register",
        params={"username": "someone", "password": "Aa1$abcd"},
    )
    assert response.json()["status"] == -1


def test_sensitive_form_fields_are_not_query_parameters():
    paths = app.openapi()["paths"]
    scoped_fields = {
        "/api/user/login": {"username"},
        "/admin/api/user/login": {"username"},
        "/api/user/register": {"username", "name", "card_id", "phone", "wechat_id", "student_id", "email"},
        "/api/user/contact": {"email", "phone", "wechat_id"},
        "/admin/api/user/contact": {"email", "phone", "wechat_id"},
        "/admin/api/member/updateUserInf": {"username", "state", "name", "student_id", "card_id", "phone", "wechat_id", "email"},
        "/admin/api/member/queryMembers": {"name", "student_id"},
        "/admin/api/member/queryReviewMembers": {"name", "student_id"},
        "/admin/api/member/queryUnsignedMembers": {"name", "student_id"},
        "/admin/api/member/queryStaffMembers": {"name"},
        "/api/user/queryEquips": {"local"},
        "/api/transfer/transferRecord": {"receive_user"},
        "/api/find/queryUserName": {"name", "student_id"},
        "/api/find/sendResetEmail": {"name", "student_id", "username"},
        "/api/staff/querySign": {"sign_code"},
        "/api/staff/finishSign": {"sign_code"},
        "/admin/api/action/reSign": {"sign_code"},
    }
    for path, fields in scoped_fields.items():
        query_names = {
            parameter["name"]
            for parameter in paths[path]["post"].get("parameters", [])
            if parameter["in"] == "query"
        }
        assert not fields & query_names, path


def test_device_only_login_and_registration_are_disabled(client):
    login = client.post("/api/user/loginByEquip", params={"equip_id": "spoofed-device"})
    assert login.json()["status"] < 0
    assert login.json()["data"] != "spoofed-device"

    register = client.post("/api/user/newEquipment", json={"equip_id": "spoofed-device"})
    assert register.json()["status"] < 0
