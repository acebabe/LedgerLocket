# LedgerLocket starter

A realistic, production-minded starter for a centralized off-chain credit ledger with:
- email/password signup + login
- admin mint flows
- wallet balance tracking
- notification system via Socket.IO
- Redis/Celery background jobs
- Playwright receipt screenshot generation
- Coinbase and Binance connector stubs
- Docker Compose development setup

Quickstart
1. Copy `.env.example` and set values.
2. Start development services:
   docker-compose up --build
3. Initialize the database:
   docker-compose exec web flask db init
   docker-compose exec web flask db migrate
   docker-compose exec web flask db upgrade
4. Use the API routes under `/auth`, `/wallets`, `/transactions`, and `/notifications`.

Important
- Never commit real secrets.
- Use a secret manager in production.
- Rotate any public credentials before sharing.

Key endpoints
- POST /auth/register
- POST /auth/login
- GET /auth/verify?token=...
- POST /auth/password-reset/request
- POST /auth/password-reset/confirm
- GET /wallets/<address>/balance
- POST /wallets/link
- POST /transactions/mint
- POST /transactions/transfer
- GET /transactions/<tx_ref>/screenshot.png

Demo admin flow
- Create an admin user in the DB with roles ["admin"], or seed one manually.
- POST /transactions/mint to credit a wallet.
- Fetch the PNG receipt from the transaction route.
