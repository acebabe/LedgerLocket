# Coinbase connector stub

class CoinbaseConnector:
    def __init__(self, credentials=None):
        self.credentials = credentials

    def start_oauth(self):
        # return authorization URL for Coinbase sandbox / production
        return 'https://www.coinbase.com/oauth/authorize?client_id=SANDBOX&response_type=code'

    def fetch_accounts(self, access_token):
        # stub: return fake accounts for sandbox
        return [{ 'id':'acct_1', 'currency':'USD', 'balance': '1000.00' }]

    def simulate_deposit(self, account_id, amount):
        # for demo purposes only
        return { 'status':'simulated', 'account_id':account_id, 'amount':amount }
