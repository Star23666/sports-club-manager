# Python Backend (FastAPI)

API-compatible with the existing frontend. Zero frontend changes required.

## Quick Start

From project root:
```bash
# Windows
.\start.ps1

# macOS / Linux
bash start.sh
```

→ Backend starts at <http://localhost:8081/docs> with **SQLite** (no MySQL needed).

Before opening the admin UI, run `cd python && python -m app.bootstrap_admin` and enter a new password at the prompt. Never pass it as a command-line argument. Existing installations with the old public admin password must run the same command to rotate it.

## Manual Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env — customize APP_NAME, ORG_NAME, etc.
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

## Configuration

See `.env.example` for all options. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_TYPE` | `sqlite` | `sqlite` (zero-config) or `mysql` |
| `SQLITE_PATH` | (empty) | Optional SQLite file path; useful for isolated local tests |
| `APP_NAME` | `Sports Club Manager` | Displayed in API docs |
| `ORG_NAME` | `My Sports Club` | Used in emails |
| `MEMBER_ID_LABEL` | `Student ID` | Label for the member ID field |
| `EMAIL_DOMAIN` | (empty) | Domain for auto-generated student emails |
| `CORS_ORIGINS` | Local client/admin URLs | Comma-separated, exact allowed frontend origins |

## API Style
- Most endpoints: `POST` + non-secret query parameters → `{ "status": int, "data": ... }`
- Token auth: `Authorization: Bearer <UUID token>` + tokens table + out_time. Query-string tokens are ignored.
- Passwords: JSON request body; Argon2id for new/changed passwords. Legacy MD5 is upgraded after correct login.
- Device-only login and new device enrollment are disabled; existing devices can still be revoked. Sign-in codes and registration/contact/profile updates use JSON bodies.
- Account-recovery routes have database-backed fixed-window limits by direct peer IP and account/code. Reverse proxies can make users share one IP bucket; do not trust `X-Forwarded-For` without a trusted-proxy configuration.
- For an existing MySQL database, run `ALTER TABLE users MODIFY password VARCHAR(255);` and `database/upgrade_recovery_rate_limit.sql` before deploying this version. SQLite initializes the new table automatically.
- The legacy password-column change and rate-limit table migration were smoke-tested against a disposable MySQL 8.0 database; reapplying the table migration was safe, and a synthetic legacy user was preserved. The opt-in test is `tests/integration/test_mysql_recovery.py` and refuses databases not named `club_upgrade_test*`.
- The opt-in full MySQL workflow test is `tests/integration/test_mysql_full_workflow.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_e2e_test*`, run `python/seed_demo.py`, set `TEST_MYSQL_WORKFLOW=1` with matching `DB_*` settings, then run `pytest tests/integration/test_mysql_full_workflow.py`. It checks member login and enrollment, duplicate enrollment, cross-member and cross-staff denial, check-in, duplicate check-in, and stale transfer rejection. Never point it at a real club database.
- Tokens with missing or malformed expiration timestamps are now rejected and removed. Anyone relying on a legacy token without an expiration must sign in again.
- Staff can now enter the member's sign-in code manually if camera scanning is unavailable. The browser-tested path covers login, roster, opening an activity, manual-code check-in, and duplicate-check-in feedback.
- Do not expose this API with real users yet: the MySQL workflow now has automated coverage, but physical camera-scanning acceptance, concurrency/capacity checks, login throttling, and a broader security review are still required.

## Docker

```bash
cd .. && docker compose up --build
```
