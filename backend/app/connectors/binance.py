# Binance connector stub

class BinanceConnector:
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret

    def test_connection(self):
        # stubbed response
        return { 'ok': True, 'mode': 'testnet' }

    def fetch_balances(self):
        return [{ 'asset': 'USDT', 'free': '500.00', 'locked': '0.00' }]

    def simulate_deposit(self, account_id, amount):
        return { 'status':'simulated', 'account_id':account_id, 'amount':amount }
