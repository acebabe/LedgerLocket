from decimal import Decimal
from uuid import uuid4

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import AuditLog, Notification, Transaction, Wallet, db
from tasks import queue_notification

bp = Blueprint("transactions", __name__)


def require_admin(user_id):
    from models import User

    user = User.query.get(user_id)
    return bool(user and "admin" in (user.roles or []))


@bp.route("/mint", methods=["POST"])
@jwt_required()
def mint():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({"msg": "admin required"}), 403

    data = request.get_json() or {}
    to_address = data.get("to_address")
    amount = Decimal(str(data.get("amount", "0")))
    memo = data.get("memo", "")

    if not to_address or amount <= 0:
        return jsonify({"msg": "to_address and positive amount required"}), 400

    wallet = Wallet.query.filter_by(address=to_address).first()
    if not wallet:
        wallet = Wallet(address=to_address, balance=0)
        db.session.add(wallet)

    wallet.balance = wallet.balance + amount
    tx = Transaction(
        tx_ref=str(uuid4()),
        from_address=None,
        to_address=to_address,
        amount=amount,
        type="mint",
        data={"memo": memo},
    )
    db.session.add(tx)

    notif = Notification(
        wallet_address=to_address,
        type="credit_received",
        payload={"amount": str(amount), "memo": memo, "tx_ref": tx.tx_ref},
    )
    db.session.add(notif)

    audit = AuditLog(
        actor_id=user_id,
        action="mint",
        object_type="wallet",
        object_id=to_address,
        reason=memo,
    )
    db.session.add(audit)
    db.session.commit()

    queue_notification(notif.id)
    return jsonify({"msg": "minted", "tx_ref": tx.tx_ref}), 201


@bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
    data = request.get_json() or {}
    from_addr = data.get("from_address")
    to_addr = data.get("to_address")
    amount = Decimal(str(data.get("amount", "0")))

    if not from_addr or not to_addr or amount <= 0:
        return jsonify({"msg": "from_address, to_address, and amount required"}), 400

    w_from = Wallet.query.filter_by(address=from_addr).first()
    if not w_from or w_from.balance < amount:
        return jsonify({"msg": "insufficient balance"}), 400

    w_to = Wallet.query.filter_by(address=to_addr).first()
    if not w_to:
        w_to = Wallet(address=to_addr, balance=0)
        db.session.add(w_to)

    w_from.balance = w_from.balance - amount
    w_to.balance = w_to.balance + amount

    tx = Transaction(
        tx_ref=str(uuid4()),
        from_address=from_addr,
        to_address=to_addr,
        amount=amount,
        type="transfer",
    )
    db.session.add(tx)

    notif = Notification(
        wallet_address=to_addr,
        type="credit_received",
        payload={"amount": str(amount), "from": from_addr},
    )
    db.session.add(notif)
    db.session.commit()

    queue_notification(notif.id)
    return jsonify({"msg": "transferred", "tx_ref": tx.tx_ref})
