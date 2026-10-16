# LedgerLocket — scaffold

This repository contains an initial scaffold for LedgerLocket: a centralized non-withdrawable credits platform.

What's included in this scaffold branch:

- Flask backend (backend/) with basic models, a mint endpoint, and a Playwright-based receipt PNG endpoint.
- Connector stubs for Coinbase and Binance (backend/app/connectors).
- Docker Compose for local development (Postgres, Redis, web, worker).
- OpenAPI starter (openapi.yaml).

Quick start (dev):

1. Copy `.env.example` to `.env` and customize if needed.
2. Start services:
   docker-compose up --build

3. Create the DB & run migrations (inside the `web` container):
   flask db init
   flask db migrate
   flask db upgrade

4. Optionally install Playwright browsers locally for testing:
   python -m playwright install chromium

Notes:
- This is a minimal scaffold to get you started. The system is NOT production-ready. You should add secure secret management, encrypted storage for credentials, RBAC, tests, and CI.
