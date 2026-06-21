"""
Seed the database with demo data for exploring the UI.

Usage:
    .venv/Scripts/python python/seed_demo.py       # Windows
    .venv/bin/python python/seed_demo.py            # macOS / Linux

Requires: backend running or at least the DB accessible.
Defaults to SQLite (badminton.db in project root).
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.db import engine, tx, exec_one, fetch_one
from app.utils import encrypt_md5

PWD = encrypt_md5("Aa1$abcd")  # default demo password

DEMO_USERS = [
    # (username, name, student_id, state, role)
    ("zhangsan", "Zhang San", "S2024001", 2, "member"),
    ("lisi", "Li Si", "S2024002", 2, "member"),
    ("wangwu", "Wang Wu", "S2024003", 2, "member"),
    ("zhaoliu", "Zhao Liu", "S2024004", 2, "member"),
    ("staff01", "Staff Chen", "T2024001", 3, "staff"),
    ("staff02", "Staff Huang", "T2024002", 3, "staff"),
]

DEMO_ACTIONS = [
    {
        "title": "Tuesday Night Session",
        "place": "Gym Court A",
        "time_range": "20:00-22:00",
        "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "max_num": 4,
        "state": 2,  # open for registration
        "open_time": datetime.now() - timedelta(days=1),
        "close_time": datetime.now() + timedelta(days=1),
    },
    {
        "title": "Weekend Free Play",
        "place": "Gym Court B",
        "time_range": "14:00-17:00",
        "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "max_num": 6,
        "state": 2,
        "open_time": datetime.now(),
        "close_time": datetime.now() + timedelta(days=3),
    },
    {
        "title": "Training Camp #12",
        "place": "Main Court",
        "time_range": "09:00-12:00",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "max_num": 3,
        "state": 2,
        "open_time": datetime.now() - timedelta(days=2),
        "close_time": datetime.now() + timedelta(hours=12),
    },
]


def main():
    with tx() as conn:
        # ── Create demo users ────────────────────────
        for username, name, sid, state, _role in DEMO_USERS:
            exists = fetch_one(conn, "select id from users where username=:u", {"u": username})
            if exists:
                print(f"  SKIP  user '{username}' already exists")
                continue
            exec_one(
                conn,
                """INSERT INTO users (username, password, name, student_id, state, phone, email, wechat_id)
                   VALUES (:u, :p, :n, :sid, :st, :ph, :em, :wx)""",
                {
                    "u": username, "p": PWD, "n": name, "sid": sid,
                    "st": state, "ph": "+8613800000000", "em": f"{username}@example.com", "wx": f"wx_{username}",
                },
            )
            print(f"  +OK   user '{username}' (state={state})")

        # ── Create demo actions ───────────────────────
        for a in DEMO_ACTIONS:
            exists = fetch_one(conn, "select id from actions where title=:t and date=:d", {"t": a["title"], "d": a["date"]})
            if exists:
                print(f"  SKIP  action '{a['title']}' already exists")
                continue
            # Assign first staff member
            staff = fetch_one(conn, "select id from users where state=3 limit 1")
            staff_id = staff["id"] if staff else 1
            exec_one(
                conn,
                """INSERT INTO actions (title, place, time_range, date, max_num, state, open_time, close_time, staff_user_id, wechat_url)
                   VALUES (:t, :pl, :tr, :d, :mn, :st, :ot, :ct, :sid, :wu)""",
                {
                    "t": a["title"], "pl": a["place"], "tr": a["time_range"],
                    "d": a["date"], "mn": a["max_num"], "st": a["state"],
                    "ot": a["open_time"], "ct": a["close_time"],
                    "sid": staff_id, "wu": "https://wechat.group/example",
                },
            )
            print(f"  +OK   action '{a['title']}' ({a['date']})")

    print(f"\nDone. Demo password for all users: Aa1$abcd")
    print("Admin login: admin / admin")
    print("Start the backend to explore: http://localhost:8081/docs")


if __name__ == "__main__":
    main()
