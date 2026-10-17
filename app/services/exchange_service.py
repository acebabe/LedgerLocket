class ExchangeAdapter:
    name = "base"

    def __init__(self, config=None):
        self.config = config or {}

    def ping(self):
        raise NotImplementedError

    def get_balance(self, currency):
        raise NotImplementedError

    def create_deposit(self, currency, amount):
        raise NotImplementedError


class CoinbaseAdapter(ExchangeAdapter):
    name = "coinbase"

    def ping(self):
        return {"status": "ok", "provider": "coinbase"}

    def get_balance(self, currency):
        return {"currency": currency, "balance": 0.0}

    def create_deposit(self, currency, amount):
        return {"provider": "coinbase", "currency": currency, "amount": amount, "status": "queued"}
