from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def vo(status: int, data: Any = None) -> dict:
    return {"status": status, "data": data}


def vo_json(status: int, data: Any = None) -> JSONResponse:
    # Keep keys stable, and let FastAPI handle encoding.
    return JSONResponse(content=vo(status, data))
