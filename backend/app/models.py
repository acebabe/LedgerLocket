from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    roles = db.Column(db.JSON, default=[])
    phone = db.Column(db.String(50))
    verified_email = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(128), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    label = db.Column(db.String(255))
    balance = db.Column(db.Numeric, default=0)
    metadata = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flagged = db.Column(db.Boolean, default=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(64), unique=True, nullable=False)
    from_addr = db.Column(db.String(128))
    to_addr = db.Column(db.String(128))
    amount = db.Column(db.Numeric, default=0)
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    data = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer)
    action = db.Column(db.String(255))
    object_type = db.Column(db.String(255))
    object_id = db.Column(db.String(255))
    reason = db.Column(db.Text)
    metadata = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
