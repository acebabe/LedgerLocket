"""
Coinbase connector stub.

NOTE:
- This file provides a sandboxed connector skeleton and does NOT contain real credentials.
- Store client_id/secret in a KMS / encrypted store and reference them via environment variables.
"""
import os
import logging

class CoinbaseConnector:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("COINBASE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("COINBASE_CLIENT_SECRET")
        # Additional HTTP client setup (requests or aiohttp)

    def start_oauth_flow(self, redirect_uri, state):
        """
        Return URL to redirect users to Coinbase OAuth (sandbox / production).
        """
        # Compose OAuth URL using client_id, redirect_uri and scopes.
        return "https://www.coinbase.com/oauth/authorize?response_type=code&client_id={}&redirect_uri={}&state={}".format(self.client_id, redirect_uri, state)

    def exchange_code(self, code, redirect_uri):
        """
        Exchange auth code for tokens (stub).
        """
        # Implement POST to Coinbase token endpoint -> store tokens encrypted
        logging.info("Exchange code called (stub): %s", code)
        return {"access_token": "sandbox_token", "refresh_token": "sandbox_refresh"}

    def fetch_accounts(self, access_token):
        """
        Fetch linked coinbase accounts (stub).
        """
        # In production call Coinbase API
        return [{"id":"acct_sandbox_1","currency":"BTC","balance":"0.0"}]

    def simulate_credit(self, account_id, amount, memo=""):
        """
        Admin-only sandbox simulation: mark an account as credited in our ledger (no real funds).
        """
        return {"status":"ok","account_id": account_id, "amount": amount, "memo": memo}