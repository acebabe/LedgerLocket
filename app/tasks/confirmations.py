# app/tasks/confirmations.py
import time
from web3 import Web3
from app import create_app
from app.extensions import db
from app.models.transaction import Transaction
from app.services.ledger_service import LedgerService
from app.services.notification_service import NotificationService

CONFIRMATIONS_REQUIRED = 2
SLEEP_INTERVAL = 15


def run_confirmation_watcher():
    app = create_app()
    w3 = Web3(Web3.HTTPProvider(app.config['WEB3_PROVIDER_URL']))
    ns = NotificationService(app)
    with app.app_context():
        while True:
            pending = Transaction.query.filter(Transaction.status.in_(['sent', 'simulated'])).all()
            for tx in pending:
                if not tx.tx_hash:
                    continue
                try:
                    receipt = w3.eth.get_transaction_receipt(tx.tx_hash)
                except Exception:
                    receipt = None
                if receipt and receipt.blockNumber is not None:
                    latest = w3.eth.block_number
                    confs = latest - receipt.blockNumber + 1
                    if confs >= CONFIRMATIONS_REQUIRED:
                        tx.status = 'confirmed'
                        db.session.commit()
                        # optional: credit after confirmations, if you prefer not to credit immediately
                        # LedgerService.credit(tx.to_address, float(tx.amount), reason='onchain_confirmed', related_tx_id=tx.id, locked=True)
                        ns.notify_address(tx.to_address, f'Onchain confirmation received for {tx.tx_hash} ({confs} confs).', tx_id=tx.id, email=None)
            time.sleep(SLEEP_INTERVAL)
