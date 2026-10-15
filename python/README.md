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
| `APP_NAME` | `Sports Club Manager` | Displayed in API docs |
| `ORG_NAME` | `My Sports Club` | Used in emails |
| `MEMBER_ID_LABEL` | `Student ID` | Label for the member ID field |
| `EMAIL_DOMAIN` | (empty) | Domain for auto-generated student emails |
| `CORS_ORIGINS` | Local client/admin URLs | Comma-separated, exact allowed frontend origins |

## API Style
- Most endpoints: `POST` + non-secret query parameters → `{ "status": int, "data": ... }`
- Token auth: `Authorization: Bearer <UUID token>` + tokens table + out_time. Query-string tokens are ignored.
- Passwords: JSON request body; Argon2id for new/changed passwords. Legacy MD5 is upgraded after correct login.
- Do not expose this API with real users yet: one-tap equipment login, sign-in codes, some personal information in query strings, and authorization boundaries still need review.

## Docker

```bash
cd .. && docker compose up --build
```
