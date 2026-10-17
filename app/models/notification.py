from app.extensions import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(256), nullable=True)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
