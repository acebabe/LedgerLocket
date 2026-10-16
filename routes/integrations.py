from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Integration, db
from utils.security import decrypt_text, encrypt_text

bp = Blueprint("integrations", __name__)


@bp.route("/exchange/link", methods=["POST"])
@jwt_required()
def link_exchange():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    exchange = data.get("exchange")
    credentials = data.get("credentials")
    if not exchange or not credentials:
        return jsonify({"msg": "exchange and credentials required"}), 400

    item = Integration(exchange_name=exchange, credentials_encrypted=encrypt_text(credentials), status="linked")
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id, "exchange": item.exchange_name}), 201


@bp.route("/exchange/<int:integration_id>/test", methods=["GET"])
@jwt_required()
def test_integration(integration_id):
    item = Integration.query.get(integration_id)
    if not item:
        return jsonify({"msg": "not found"}), 404
    try:
        decrypted = decrypt_text(item.credentials_encrypted)
        return jsonify({"status": "ok", "exchange": item.exchange_name, "credentials_preview": decrypted[:80]})
    except Exception:
        return jsonify({"msg": "decrypt_failed"}), 400
