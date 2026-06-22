# Contributing

Thanks for considering contributing! This is an open-source sports club management system — pull requests welcome.

## Getting Started

```bash
# 1. Fork & clone
git clone https://github.com/JosephHu04/sports-club-manager.git
cd sports-club-manager

# 2. Start backend (zero-config)
bash start.sh          # or .\start.ps1 on Windows

# 3. Run tests
pip install pytest httpx
pytest tests/ -v
```

## What to Work On

Check the [Roadmap](README.md#-roadmap) in the README, or:

- **Good first issues:** i18n English translation, better error messages, input validation
- **Security:** bcrypt migration, JWT tokens, rate limiting
- **Features:** WebSocket waitlist notifications, mobile PWA, statistics dashboard
- **Testing:** more integration tests, frontend e2e tests
- **Docs:** API examples, deployment guides for cloud platforms

## Conventions

- **Backend:** Type hints required. Use `fetch_one`/`fetch_all`/`exec_one` from `app.db`.
- **Frontend:** Vue 3 Composition API. Use the existing component patterns.
- **SQL:** Use dialect-agnostic helpers (`sql_binary` from `app.db`, Python-side `%` wrapping for LIKE).

## Pull Requests

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make changes + tests
3. Run `pytest tests/ -v` — all tests must pass
4. Open a PR with a clear description

## Questions?

Open an issue or discussion — happy to help!
