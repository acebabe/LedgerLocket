from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db, Wallet

bp = Blueprint("wallets", __name__)


@bp.route("/link", methods=["POST"])
@jwt_required()
def link_wallet():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    address = data.get("address")
    label = data.get("label")
    if not address:
        return jsonify({"msg": "address required"}), 400

    wallet = Wallet.query.filter_by(address=address).first()
    if wallet:
        wallet.user_id = user_id
        wallet.label = label or wallet.label
        db.session.commit()
        return jsonify({"address": wallet.address, "balance": str(wallet.balance)})

    wallet = Wallet(address=address, label=label, user_id=user_id, balance=0)
    db.session.add(wallet)
    db.session.commit()
    return jsonify({"address": wallet.address, "balance": str(wallet.balance)}), 201


@bp.route("/<address>/balance", methods=["GET"])
def balance(address):
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        return jsonify({"address": address, "balance": "0"})
    return jsonify({"address": address, "balance": str(wallet.balance)})
