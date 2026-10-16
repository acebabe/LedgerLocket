import logging
import os


class BinanceConnector:
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

    def validate_keys(self):
        logging.info("Validating binance keys (stub)")
        return True

    def fetch_account(self):
        return {"balances": [{"asset": "BTC", "free": "0.0", "locked": "0.0"}]}

    def simulate_credit(self, account_id, amount):
        logging.info("Simulating credit on Binance testnet (stub)")
        return {"status": "ok", "account_id": account_id, "amount": amount}
