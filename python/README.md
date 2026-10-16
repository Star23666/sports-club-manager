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
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload --no-proxy-headers
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
| `LOGIN_ACCOUNT_LIMIT` | `8` | Attempts per username per fixed window, shared by member/admin login |
| `LOGIN_IP_LIMIT` | `120` | Attempts per direct peer IP per fixed window |
| `LOGIN_WINDOW_SECONDS` | `900` | Login limit window length in seconds |
| `TRUSTED_PROXY_IPS` | (empty) | Optional comma-separated **exact** IPs of proxies that overwrite `X-Real-IP`; no CIDRs |

## API Style
- Most endpoints: `POST` + non-secret query parameters → `{ "status": int, "data": ... }`
- Token auth: `Authorization: Bearer <UUID token>` + tokens table + out_time. Query-string tokens are ignored.
- Passwords: JSON request body; Argon2id for new/changed passwords. Legacy MD5 is upgraded after correct login.
- A successful member/admin self-service password change, administrator password reset, or recovery-code reset deletes that account's existing tokens in the same transaction. The affected user must sign in again. A recovery code is rechecked under a database row lock so concurrent submissions cannot both succeed.
- Administrator role/status edits, account approval, credit restoration/recalculation, action completion penalties, and late sign-in restoration revoke the affected user's tokens when the account state actually changes. A profile edit with unchanged state keeps the session. Re-login is required to use any newly granted role; no database migration is needed.
- Credit restoration/recalculation is limited to active or credit-restricted members (states 2 and 1); it cannot lift an account ban (state 0). The credit-management list excludes banned accounts. Unbanning remains an explicit account-management decision.
- The review-approval endpoint accepts only pending accounts (state -1), matching new registrations and the review list. It cannot approve a banned account (state 0); use an explicit account-management state edit for unbanning.
- Device-only login and new device enrollment are disabled; existing devices can still be revoked. Sign-in codes and registration/contact/profile updates use JSON bodies.
- Account-recovery routes have database-backed fixed-window limits by peer IP and account/code. All bundled launchers disable Uvicorn proxy-header processing; keep `--no-proxy-headers` if starting it manually. By default, forwarded headers are ignored. To distinguish clients behind a controlled proxy, explicitly list only its **exact current peer IP(s)** in `TRUSTED_PROXY_IPS`. Only then is one valid `X-Real-IP` accepted; missing, duplicate, or malformed values fall back to the peer bucket. The bundled Nginx config overwrites `X-Real-IP` with `$remote_addr`; never enable this option for a proxy that merely forwards user-supplied headers. Docker container IPs can change after recreation, so revalidate them before using this opt-in. `X-Forwarded-For` is never trusted for rate limiting.
- Member and admin login attempts share database-backed fixed-window limits (default: 8/account and 120/direct-peer IP per 900 seconds, configurable through `LOGIN_*` settings). Failed attempts consume quota; a successful login clears the account bucket but not the IP bucket. The same direct-peer limitation applies behind reverse proxies.
- For an existing MySQL database, run `ALTER TABLE users MODIFY password VARCHAR(255);`, `database/upgrade_recovery_rate_limit.sql`, and `database/upgrade_login_rate_limit.sql` before deploying this version. SQLite initializes both tables automatically. Login fails closed if the new table is missing.
- The legacy password-column change and rate-limit table migration were smoke-tested against a disposable MySQL 8.0 database; reapplying the table migration was safe, and a synthetic legacy user was preserved. The opt-in test is `tests/integration/test_mysql_recovery.py` and refuses databases not named `club_upgrade_test*`.
- The opt-in full MySQL workflow test is `tests/integration/test_mysql_full_workflow.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_e2e_test*`, run `python/seed_demo.py`, set `TEST_MYSQL_WORKFLOW=1` with matching `DB_*` settings, then run `pytest tests/integration/test_mysql_full_workflow.py`. It checks member login and enrollment, duplicate enrollment, cross-member and cross-staff denial, check-in, duplicate check-in, and stale transfer rejection. Never point it at a real club database.
- The opt-in MySQL concurrency test is `tests/integration/test_mysql_capacity.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_capacity_test_*`, set `TEST_MYSQL_CAPACITY=1` and matching `DB_*` settings, then run that test. It races six members for one seat, checks unique waiting ranks, tests the MySQL login counter, races two members to accept one public transfer, and verifies that two simultaneous password resets cannot reuse one code or preserve an old session. SQLite runs the equivalent concurrency scenarios by default. On a disposable MySQL database, both rate-limit tables were removed, both upgrade scripts were then applied twice, and existing user rows remained intact.
- The opt-in MySQL role test is `tests/integration/test_mysql_role_sessions.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_role_test_*`, set `TEST_MYSQL_ROLES=1` and matching `DB_*` settings, then run it. It verifies that member-to-staff promotion and absence penalties invalidate old sessions, while the administrator remains signed in.
- The opt-in MySQL check-in race test is `tests/integration/test_mysql_checkin_completion.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_checkin_test_*`, set `TEST_MYSQL_CHECKIN=1` and matching `DB_*` settings, then run it. It races staff check-in against staff/admin action completion and verifies that the sign-in record agrees with the member's absence count. SQLite runs the same two races by default.
- The opt-in MySQL admin-lifecycle race test is `tests/integration/test_mysql_admin_lifecycle.py`. Apply `database/install.sql` to a **fresh disposable** database named `club_lifecycle_test_*`, set `TEST_MYSQL_ADMIN_LIFECYCLE=1` and matching `DB_*` settings, then run it. It races registration closure against waitlisting and an administrator edit against the staff check-in start; SQLite runs both regressions by default.
- Tokens with missing or malformed expiration timestamps are now rejected and removed. Anyone relying on a legacy token without an expiration must sign in again.
- Staff can now enter the member's sign-in code manually if camera scanning is unavailable. The browser-tested path covers login, roster, opening an activity, manual-code check-in, and duplicate-check-in feedback.
- Do not expose this API with real users yet: MySQL workflow, capacity, transfer, and check-in/completion races now have automated coverage, but physical camera-scanning acceptance, end-to-end proxy/IP testing in the target deployment, load testing, and a broader security review are still required. These concurrency tests are narrow regressions, not production load tests.

## Docker

```bash
cd .. && docker compose up --build
```

Docker Compose now binds the backend's diagnostic port to `127.0.0.1:8081` on the host. The member and admin Nginx containers still reach it over the internal Docker network. This is a local preview layout, not an HTTPS production deployment.
