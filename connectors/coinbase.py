import os
import logging


class CoinbaseConnector:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("COINBASE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("COINBASE_CLIENT_SECRET")

    def start_oauth_flow(self, redirect_uri, state):
        return (
            "https://www.coinbase.com/oauth/authorize?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={redirect_uri}&state={state}"
        )

    def exchange_code(self, code, redirect_uri):
        logging.info("Exchange code called (stub): %s", code)
        return {"access_token": "sandbox_token", "refresh_token": "sandbox_refresh"}

    def fetch_accounts(self, access_token):
        return [{"id": "acct_sandbox_1", "currency": "BTC", "balance": "0.0"}]

    def simulate_credit(self, account_id, amount, memo=""):
        return {"status": "ok", "account_id": account_id, "amount": amount, "memo": memo}
