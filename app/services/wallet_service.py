from web3 import Web3
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self, app_or_cfg):
        cfg = app_or_cfg.config if hasattr(app_or_cfg, 'config') else app_or_cfg
        self.provider = cfg.get('WEB3_PROVIDER_URL')
        self.private_key = cfg.get('WALLET_PRIVATE_KEY')
        self.gas_price = cfg.get('GAS_PRICE_GWEI', 20)
        self.broadcast = cfg.get('BROADCAST_TX', False)
        self.w3 = Web3(Web3.HTTPProvider(self.provider))

    def send_native_token(self, to_address, amount_eth: Decimal, chain_id: int):
        if not self.w3.is_connected():
            return {'status':'error', 'error':'provider_unreachable'}
        account = self.w3.eth.account.from_key(self.private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        gas_price = self.w3.to_wei(float(self.gas_price), 'gwei')
        value = self.w3.to_wei(amount_eth, 'ether')
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': value,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
        signed = account.sign_transaction(tx)
        if not self.broadcast:
            return {'status':'simulated', 'tx_hash': signed.hash.hex() if hasattr(signed, 'hash') else None, 'from': account.address}
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            return {'status':'sent', 'tx_hash': tx_hash.hex(), 'from': account.address}
        except Exception as e:
            logger.exception('broadcast failed')
            return {'status':'error', 'error': str(e)}
