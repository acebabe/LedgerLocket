from app.extensions import db
from app.models.ledger_account import LedgerAccount
from app.models.ledger_entry import LedgerEntry
from app.models.transaction import Transaction
from sqlalchemy import func

class LedgerService:
    @staticmethod
    def credit(address, amount, reason=None, related_tx_id=None, locked=True):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        if not acct:
            acct = LedgerAccount(owner_address=address, balance=0.0)
            db.session.add(acct)
            db.session.flush()
        acct.balance = float(acct.balance or 0.0) + float(amount)
        entry = LedgerEntry(account_id=acct.id, delta=float(amount), balance_after=acct.balance, reason=reason, related_tx_id=related_tx_id, locked=locked)
        db.session.add(entry)
        db.session.commit()
        return acct, entry

    @staticmethod
    def debit(address, amount, reason=None, related_tx_id=None):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        if not acct or acct.balance < amount:
            raise ValueError('insufficient_funds')
        acct.balance = float(acct.balance) - float(amount)
        entry = LedgerEntry(account_id=acct.id, delta=-float(amount), balance_after=acct.balance, reason=reason, related_tx_id=related_tx_id, locked=False)
        db.session.add(entry)
        db.session.commit()
        return acct, entry

    @staticmethod
    def get_balance(address):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        return acct.balance if acct else 0.0

    @staticmethod
    def get_locked_balance(address):
        acct = LedgerAccount.query.filter_by(owner_address=address).first()
        if not acct:
            return 0.0
        locked_sum = db.session.query(func.coalesce(func.sum(LedgerEntry.delta),0)).filter(LedgerEntry.account_id==acct.id, LedgerEntry.locked==True).scalar()
        return float(locked_sum or 0.0)
