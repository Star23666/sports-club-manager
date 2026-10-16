"""
SQLite-compatible schema DDL (auto-run on first startup when DB_TYPE=sqlite).

Each statement is executed with INSERT OR IGNORE / IF NOT EXISTS
so the schema is safe to run repeatedly.
"""

SCHEMA_DDL = [
    # ── Tables ──────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        name TEXT,
        card_id TEXT,
        phone TEXT,
        state INTEGER DEFAULT 0,
        wechat_id TEXT,
        email TEXT,
        student_id TEXT,
        unsigned_num INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tokens (
        user_id INTEGER PRIMARY KEY,
        token TEXT,
        out_time TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        place TEXT,
        time_range TEXT,
        date TEXT,
        max_num INTEGER,
        state INTEGER,
        open_time TEXT,
        close_time TEXT,
        staff_user_id INTEGER,
        wechat_url TEXT,
        borrow_num INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action_id INTEGER,
        sign_code TEXT,
        state INTEGER,
        borrow INTEGER DEFAULT 0,
        sign_time TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        equip_id TEXT,
        user_id INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transfer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        send_user_id INTEGER,
        receive_user_id INTEGER,
        record_id INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS waiting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action_id INTEGER,
        rank INTEGER,
        borrow INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS verifycode (
        user_id INTEGER PRIMARY KEY,
        code TEXT,
        out_time TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS recovery_rate_limit (
        bucket_key TEXT PRIMARY KEY,
        window_start INTEGER NOT NULL,
        hits INTEGER NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS recovery_rate_limit_window_idx
    ON recovery_rate_limit(window_start)
    """,

    # ── Views (drop + recreate) ─────────────────────────────
    """
    DROP VIEW IF EXISTS user_view
    """,
    """
    CREATE VIEW user_view AS
    SELECT id, username, name, phone, state, wechat_id, email, student_id, card_id, unsigned_num
    FROM users
    """,
    """
    DROP VIEW IF EXISTS record_view
    """,
    """
    CREATE VIEW record_view AS
    SELECT
        u.name AS account_name,
        r.user_id AS account_id,
        u.student_id AS account_student_id,
        a.title AS action_title,
        a.place AS action_place,
        a.date AS action_date,
        a.time_range AS action_time_range,
        a.state AS action_state,
        r.borrow,
        r.id,
        r.sign_code,
        r.state
    FROM users u
    JOIN records r ON u.id = r.user_id
    JOIN actions a ON a.id = r.action_id
    """,
    """
    DROP VIEW IF EXISTS staff_action_view
    """,
    """
    CREATE VIEW staff_action_view AS
    SELECT
        a.id,
        a.title AS action_title,
        a.date AS action_date,
        a.time_range AS action_time_range,
        a.place AS action_place,
        a.state AS action_state,
        a.borrow_num,
        a.staff_user_id AS staff_id,
        u.name AS staff_name,
        u.username AS staff_username
    FROM actions a
    JOIN users u ON a.staff_user_id = u.id
    """,
    """
    DROP VIEW IF EXISTS staff_member_view
    """,
    """
    CREATE VIEW staff_member_view AS
    SELECT
        a.id AS action_id,
        u.name,
        u.student_id,
        u.phone,
        u.wechat_id,
        r.borrow
    FROM actions a
    JOIN records r ON a.id = r.action_id
    JOIN users u ON r.user_id = u.id
    """,
    """
    DROP VIEW IF EXISTS transfer_view
    """,
    """
    CREATE VIEW transfer_view AS
    SELECT
        t.id,
        a.title AS action_title,
        us.name AS send_user,
        us.id AS send_user_id,
        ur.name AS receive_user,
        ur.id AS receive_user_id
    FROM transfer t
    JOIN records r ON t.record_id = r.id
    JOIN actions a ON r.action_id = a.id
    JOIN users us ON t.send_user_id = us.id
    JOIN users ur ON t.receive_user_id = ur.id
    """,
    """
    DROP VIEW IF EXISTS waiting_view
    """,
    """
    CREATE VIEW waiting_view AS
    SELECT
        w.id,
        a.title AS action_title,
        u.name AS action_user,
        w.rank AS wait_rank,
        w.user_id
    FROM waiting w
    JOIN actions a ON a.id = w.action_id
    JOIN users u ON u.id = w.user_id
    """,

]
