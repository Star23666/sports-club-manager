from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    action,
    admin_action,
    admin_member,
    admin_user,
    find,
    staff,
    transfer,
    user,
    waiting,
)

from .settings import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(action.router)
app.include_router(waiting.router)
app.include_router(transfer.router)
app.include_router(staff.router)
app.include_router(find.router)
app.include_router(admin_user.router)
app.include_router(admin_member.router)
app.include_router(admin_action.router)
