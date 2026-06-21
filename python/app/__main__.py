from __future__ import annotations

import uvicorn

from .settings import settings


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.port),
        reload=True,
    )


if __name__ == "__main__":
    main()
