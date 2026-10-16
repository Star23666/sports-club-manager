"""Only a specifically trusted reverse proxy may supply the rate-limit IP."""

import pytest
from pydantic import ValidationError
from starlette.requests import Request

from app.rate_limit import recovery_client_ip
from app.settings import Settings, settings


def make_request(peer: str, *real_ip_headers: str, forwarded: str | None = None) -> Request:
    headers = [(b"x-real-ip", value.encode()) for value in real_ip_headers]
    if forwarded is not None:
        headers.append((b"x-forwarded-for", forwarded.encode()))
    return Request({"type": "http", "client": (peer, 1234), "headers": headers})


def test_proxy_trust_defaults_off_and_requires_exact_valid_addresses():
    config = Settings(_env_file=None, TRUSTED_PROXY_IPS="")
    assert config.trusted_proxy_addresses == frozenset()
    config = Settings(_env_file=None, TRUSTED_PROXY_IPS="192.0.2.10, 2001:db8::10")
    assert len(config.trusted_proxy_addresses) == 2
    with pytest.raises(ValidationError):
        Settings(_env_file=None, TRUSTED_PROXY_IPS="192.0.2.0/24")
    with pytest.raises(ValidationError):
        Settings(_env_file=None, TRUSTED_PROXY_IPS="not-an-ip")


def test_untrusted_peer_cannot_spoof_rate_limit_address(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxy_ips", "192.0.2.10")
    request = make_request("198.51.100.4", "203.0.113.8", forwarded="203.0.113.9")
    assert recovery_client_ip(request) == "198.51.100.4"


def test_trusted_peer_accepts_only_one_valid_overwritten_header(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxy_ips", "192.0.2.10")
    assert recovery_client_ip(
        make_request("192.0.2.10", "203.0.113.8", forwarded="1.2.3.4, 203.0.113.8")
    ) == "203.0.113.8"
    assert recovery_client_ip(make_request("192.0.2.10", forwarded="203.0.113.8")) == "192.0.2.10"
    assert recovery_client_ip(make_request("192.0.2.10", "203.0.113.8, 198.51.100.1")) == "192.0.2.10"
    assert recovery_client_ip(make_request("192.0.2.10", "not-an-ip")) == "192.0.2.10"
    assert recovery_client_ip(make_request("192.0.2.10", "203.0.113.8", "203.0.113.9")) == "192.0.2.10"


def test_unconfigured_proxy_stays_on_shared_peer_bucket(monkeypatch):
    monkeypatch.setattr(settings, "trusted_proxy_ips", "")
    assert recovery_client_ip(make_request("192.0.2.10", "203.0.113.8")) == "192.0.2.10"
