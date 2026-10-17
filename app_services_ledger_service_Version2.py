from app.extensions import db
from app.models.ledger_account import LedgerAccount
from app.models.ledger_entry import LedgerEntry
from sqlalchemy import func
from datetime import datetime


class LedgerService:
    @staticmethod
    def _ensure_account(address, currency="ETH"):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        if not acct:
            acct = LedgerAccount(owner_address=address, balance=0.0, locked_balance=0.0, currency=currency)
            db.session.add(acct)
            db.session.flush()
        return acct

    @staticmethod
    def credit(address, amount, reason=None, related_tx_id=None, locked=True):
        acct = LedgerService._ensure_account(address)
        # update balances
        acct.balance = float(acct.balance or 0.0) + float(amount)
        if locked:
            acct.locked_balance = float(acct.locked_balance or 0.0) + float(amount)
        entry = LedgerEntry(
            account_id=acct.id,
            delta=float(amount),
            balance_after=acct.balance,
            reason=reason,
            related_tx_id=related_tx_id,
            locked=locked,
            created_at=datetime.utcnow()
        )
        db.session.add(entry)
        db.session.commit()
        return acct, entry

    @staticmethod
    def debit(address, amount, reason=None, related_tx_id=None, unlock_if_possible=False):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        if not acct or acct.balance < amount:
            raise ValueError("insufficient_funds")
        # prefer to remove from unlocked balance first
        unlocked_balance = float(acct.balance) - float(acct.locked_balance or 0.0)
        if unlocked_balance < amount and not unlock_if_possible:
            raise ValueError("insufficient_unlocked_funds")
        acct.balance = float(acct.balance) - float(amount)
        # if there is locked balance and we must reduce it (unlock_if_possible true)
        if acct.locked_balance and unlock_if_possible:
            reduction = min(float(acct.locked_balance), float(amount))
            acct.locked_balance = float(acct.locked_balance) - reduction
        entry = LedgerEntry(
            account_id=acct.id,
            delta=-float(amount),
            balance_after=acct.balance,
            reason=reason,
            related_tx_id=related_tx_id,
            locked=False
        )
        db.session.add(entry)
        db.session.commit()
        return acct, entry

    @staticmethod
    def get_balance(address):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        return float(acct.balance or 0.0) if acct else 0.0

    @staticmethod
    def get_locked_balance(address):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        return float(acct.locked_balance or 0.0) if acct else 0.0