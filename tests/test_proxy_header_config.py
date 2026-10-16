"""Keep all supported launch paths on the direct-peer rate-limit policy."""

from pathlib import Path

from app import __main__ as entrypoint


ROOT = Path(__file__).resolve().parents[1]


def test_python_entrypoint_disables_forwarded_headers(monkeypatch):
    seen = {}
    monkeypatch.setattr(entrypoint.uvicorn, "run", lambda *_args, **kwargs: seen.update(kwargs))
    entrypoint.main()
    assert seen["proxy_headers"] is False


def test_bundled_launchers_disable_forwarded_headers():
    for path in ("start.sh", "start.ps1", "python/Dockerfile"):
        content = (ROOT / path).read_text(encoding="utf-8")
        assert "--no-proxy-headers" in content, path
