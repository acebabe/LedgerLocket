from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db, Notification

bp = Blueprint("notifications", __name__)


@bp.route("/all", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = get_jwt_identity()
    # Demo: list from all wallet addresses belonging to the user is not implemented here.
    notifs = Notification.query.order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([{"id": n.id, "wallet": n.wallet_address, "type": n.type, "payload": n.payload} for n in notifs])


@bp.route("/mark-delivered", methods=["POST"])
@jwt_required()
def mark_delivered():
    data = request.get_json() or {}
    notif_id = data.get("id")
    n = Notification.query.get(notif_id)
    if not n:
        return jsonify({"msg": "not found"}), 404
    n.delivered = True
    db.session.commit()
    return jsonify({"msg": "updated"})
