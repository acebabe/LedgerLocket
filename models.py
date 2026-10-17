from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # store hashed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallets = db.relationship("Wallet", back_populates="user")

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), index=True, nullable=False)  # e.g., 0x...
    label = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # optional mapping
    user = db.relationship("User", back_populates="wallets")
    # Balance here is the app-controlled non-spendable credits
    balance = db.Column(db.Numeric(precision=30, scale=8), default=0)
    # metadata, verification data
    metadata = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_address = db.Column(db.String(256), nullable=True)  # optional
    to_address = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Numeric(precision=30, scale=8), nullable=False)
    type = db.Column(db.String(50), default="credit")  # credit, burn, admin_adjust
    data = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(256), index=True, nullable=False)
    type = db.Column(db.String(80))
    payload = db.Column(JSON, default={})
    delivered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)