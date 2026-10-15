"""Create the first administrator without exposing a password in the shell history."""

from __future__ import annotations

import argparse
from getpass import getpass

from sqlalchemy.engine import Connection

from .db import exec_one, fetch_one, tx
from .passwords import LEGACY_DEFAULT_ADMIN_HASH, hash_password
from .utils import PASSWORD_PATTERN


def create_or_rotate_admin(conn: Connection, username: str, password: str) -> str:
    username = username.strip()
    if not username or len(username) > 100:
        raise ValueError("Administrator username must be 1–100 characters.")
    if len(password) < 12 or not PASSWORD_PATTERN.fullmatch(password):
        raise ValueError("Use at least 12 characters with upper/lowercase letters, a digit and a symbol.")

    existing_admin = fetch_one(conn, "select * from users where state>=4 limit 1")
    if existing_admin:
        if existing_admin.get("password") == LEGACY_DEFAULT_ADMIN_HASH:
            collision = fetch_one(conn, "select ID from users where username=:name", {"name": username})
            if collision and int(collision["id"]) != int(existing_admin["id"]):
                raise ValueError("That username is already in use.")
            updated = exec_one(
                conn,
                "update users set username=:name, password=:pwd where ID=:uid and password=:old",
                {
                    "name": username,
                    "pwd": hash_password(password),
                    "uid": existing_admin["id"],
                    "old": LEGACY_DEFAULT_ADMIN_HASH,
                },
            )
            if updated != 1:
                raise ValueError("Legacy administrator changed during rotation; try again.")
            exec_one(conn, "delete from tokens where user_id=:uid", {"uid": existing_admin["id"]})
            return "rotated"
        raise ValueError("An administrator already exists; this command will not overwrite it.")

    if fetch_one(conn, "select ID from users where username=:name", {"name": username}):
        raise ValueError("That username is already in use.")
    exec_one(
        conn,
        "insert into users(username, password, name, state) values (:name, :pwd, :display, 4)",
        {"name": username, "pwd": hash_password(password), "display": "Administrator"},
    )
    return "created"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or rotate the first administrator")
    parser.add_argument("--username", default="admin")
    args = parser.parse_args()
    password = getpass("New administrator password: ")
    if password != getpass("Repeat password: "):
        parser.error("Passwords do not match.")
    try:
        with tx() as conn:
            action = create_or_rotate_admin(conn, args.username, password)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Administrator {action}. You can now sign in as {args.username}.")


if __name__ == "__main__":
    main()
