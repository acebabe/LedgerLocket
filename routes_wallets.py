from flask import Blueprint, request, jsonify
from models import db, Wallet
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("wallets", __name__)

@bp.route("/link", methods=["POST"])
@jwt_required()
def link_wallet():
    user_id = get_jwt_identity()
    data = request.json
    address = data.get("address")
    label = data.get("label")
    if not address:
        return {"msg": "address required"}, 400
    w = Wallet.query.filter_by(address=address).first()
    if w:
        # attach if not attached
        if w.user_id != user_id:
            w.user_id = user_id
            db.session.commit()
        return jsonify({"address": w.address, "balance": str(w.balance)})
    w = Wallet(address=address, label=label, user_id=user_id)
    db.session.add(w)
    db.session.commit()
    return jsonify({"address": w.address, "balance": str(w.balance)}), 201

@bp.route("/<address>/balance", methods=["GET"])
def balance(address):
    w = Wallet.query.filter_by(address=address).first()
    if not w:
        return {"address": address, "balance": "0"}
    return {"address": address, "balance": str(w.balance)}