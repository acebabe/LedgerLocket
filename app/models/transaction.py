from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(100), nullable=True)
    from_address = db.Column(db.String(256), nullable=True)
    to_address = db.Column(db.String(256), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    chain_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    note = db.Column(db.Text, nullable=True)
    locked = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id} {self.tx_hash}>'
