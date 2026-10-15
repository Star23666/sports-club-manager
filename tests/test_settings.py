from app.settings import Settings


def test_sqlite_is_the_zero_config_default(monkeypatch):
    monkeypatch.delenv("DB_TYPE", raising=False)
    settings = Settings(_env_file=None)

    assert settings.is_sqlite
    assert settings.sqlalchemy_url.startswith("sqlite:///")


def test_cors_origins_are_explicit_and_trimmed():
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS="http://localhost:8080, https://events.example.com, ,",
    )

    assert settings.allowed_origins == [
        "http://localhost:8080",
        "https://events.example.com",
    ]


def test_cors_does_not_accept_an_unlisted_origin(client):
    response = client.options(
        "/api/user/login",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.headers.get("access-control-allow-origin") is None
