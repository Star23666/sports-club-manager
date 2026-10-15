"""Read bearer tokens only from the Authorization header."""

from __future__ import annotations

from fastapi import Header


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        return ""
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer":
        return ""
    return token.strip()
