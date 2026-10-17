# LedgerLocket - Starter (Flask + Postgres + Redis + Playwright)

LedgerLocket is a starter scaffold for a centralized non-withdrawable credits ledger with:
- Flask API (auth, wallets, transactions)
- SQLAlchemy + Flask-Migrate
- Celery + Redis for background jobs
- Flask-SocketIO for realtime notifications
- Playwright endpoint to generate receipt PNGs
- Exchange Integration Layer stubs (coinbase, binance)
- Docker Compose for local dev

IMPORTANT: Do NOT commit real credentials. Use environment variables or a secret manager.

Quickstart (dev)
1. Copy `.env.example` to `.env` and fill values (do NOT paste production secrets here).
2. Start local services:
   docker-compose up --build
3. Create DB and run migrations:
   docker-compose exec web flask db upgrade
4. Create an admin user using the /auth/register endpoint or via flask shell.
5. Run a worker (already run by docker-compose).

Security steps
- Rotate any keys you pasted publicly.
- Use a secret manager (HashiCorp Vault, AWS Secrets Manager) for production.
- Enable 2FA for admin accounts.

Files in this repo include:
- backend/: Flask app and routes
- connectors/: exchange connector stubs
- receipts/: Playwright screenshot worker
- docker-compose.yml, Dockerfile

If you want, I can push this scaffold to a GitHub repo once you provide the repo name/owner and confirm you've rotated keys.