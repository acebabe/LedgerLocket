from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import JSON
from passlib.hash import bcrypt


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    roles = db.Column(JSON, default=lambda: ["user"])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallets = db.relationship("Wallet", back_populates="user")

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.verify(password, self.password_hash)


class Wallet(db.Model):
    __tablename__ = "wallet"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), index=True, nullable=False)
    label = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", back_populates="wallets")
    balance = db.Column(Numeric(precision=30, scale=8), default=0)
    metadata = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flagged = db.Column(db.Boolean, default=False)


class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(64), unique=True, nullable=False)
    from_address = db.Column(db.String(256), nullable=True)
    to_address = db.Column(db.String(256), nullable=False)
    amount = db.Column(Numeric(precision=30, scale=8), nullable=False)
    type = db.Column(db.String(50), default="credit")
    data = db.Column(JSON, default={})
    status = db.Column(db.String(32), default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(256), index=True, nullable=False)
    type = db.Column(db.String(80))
    payload = db.Column(JSON, default={})
    delivered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(128))
    object_type = db.Column(db.String(64))
    object_id = db.Column(db.String(64))
    reason = db.Column(db.Text, nullable=True)
    metadata = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ApiKey(db.Model):
    __tablename__ = "api_key"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    key = db.Column(db.String(255), unique=True, nullable=False)
    scopes = db.Column(JSON, default=list)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Integration(db.Model):
    __tablename__ = "integration"

    id = db.Column(db.Integer, primary_key=True)
    exchange_name = db.Column(db.String(80), nullable=False)
    credentials_encrypted = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="linked")
    last_sync = db.Column(db.DateTime, nullable=True)


class KycProfile(db.Model):
    __tablename__ = "kyc_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="pending")
    documents = db.Column(JSON, default=list)
    reviewed_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailVerification(db.Model):
    __tablename__ = "email_verification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordReset(db.Model):
    __tablename__ = "password_reset"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RefreshToken(db.Model):
    __tablename__ = "refresh_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
