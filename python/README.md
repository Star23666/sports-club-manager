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

## API Style
- Most endpoints: `POST` + QueryString params → `{ "status": int, "data": ... }`
- Token auth: `UUID token + tokens table + out_time`

## Docker

```bash
cd .. && docker compose up --build
```
