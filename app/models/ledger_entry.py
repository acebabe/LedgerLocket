from app.extensions import db
from datetime import datetime

class LedgerEntry(db.Model):
    __tablename__ = 'ledger_entries'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, index=True, nullable=False)
    delta = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    related_tx_id = db.Column(db.Integer, nullable=True)
    locked = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
