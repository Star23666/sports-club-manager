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
