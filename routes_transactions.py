from flask import Blueprint, request, jsonify
from models import db, Wallet, Transaction, Notification
from decimal import Decimal
from flask_jwt_extended import jwt_required, get_jwt_identity
from tasks import queue_notification

bp = Blueprint("transactions", __name__)

@bp.route("/mint", methods=["POST"])
@jwt_required()
def mint():
    # Admin-only in production — for demo we allow any logged-in user
    data = request.json
    to_address = data.get("to_address")
    amount = Decimal(str(data.get("amount", "0")))
    if amount <= 0:
        return {"msg": "amount must be positive"}, 400
    w = Wallet.query.filter_by(address=to_address).first()
    if not w:
        w = Wallet(address=to_address, balance=0)
        db.session.add(w)
    w.balance = w.balance + amount
    tx = Transaction(from_address=None, to_address=to_address, amount=amount, type="mint")
    db.session.add(tx)
    # create notification row
    notif = Notification(wallet_address=to_address, type="credit_received", payload={"amount": str(amount)})
    db.session.add(notif)
    db.session.commit()
    # push background notification via Celery/Redis
    queue_notification(notif.id)
    return {"msg": "minted", "to": to_address, "amount": str(amount)}, 201

@bp.route("/send", methods=["POST"])
@jwt_required()
def send():
    # Off-chain transfer between addresses within the app (non-spendable)
    data = request.json
    from_addr = data.get("from_address")
    to_addr = data.get("to_address")
    amount = Decimal(str(data.get("amount", "0")))
    if amount <= 0:
        return {"msg":"amount must be positive"}, 400
    w_from = Wallet.query.filter_by(address=from_addr).first()
    if not w_from or w_from.balance < amount:
        return {"msg":"insufficient balance"}, 400
    w_to = Wallet.query.filter_by(address=to_addr).first()
    if not w_to:
        w_to = Wallet(address=to_addr, balance=0)
        db.session.add(w_to)
    # Update balances
    w_from.balance = w_from.balance - amount
    w_to.balance = w_to.balance + amount
    tx = Transaction(from_address=from_addr, to_address=to_addr, amount=amount, type="transfer")
    db.session.add(tx)
    notif = Notification(wallet_address=to_addr, type="credit_received", payload={"amount": str(amount), "from": from_addr})
    db.session.add(notif)
    db.session.commit()
    queue_notification(notif.id)
    return {"msg":"transferred", "to": to_addr, "amount": str(amount)}