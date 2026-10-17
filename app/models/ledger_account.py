from app.extensions import db
from datetime import datetime


class LedgerAccount(db.Model):
    __tablename__ = "ledger_accounts"

    id = db.Column(db.Integer, primary_key=True)
    owner_address = db.Column(db.String(256), unique=True, nullable=False, index=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    locked_balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(32), nullable=False, default="ETH")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LedgerAccount {self.owner_address} balance={self.balance} locked={self.locked_balance}>"
