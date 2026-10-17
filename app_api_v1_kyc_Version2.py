from . import blueprint
from flask import jsonify, request
from app.models.user import User
from app.extensions import db


@blueprint.route("/kyc/status/<int:user_id>", methods=["GET"])
def get_kyc_status(user_id):
    u = User.query.get_or_404(user_id)
    return jsonify({"user_id": u.id, "kyc_status": u.kyc_status})


@blueprint.route("/kyc/status/<int:user_id>", methods=["POST"])
def set_kyc_status(user_id):
    # admin-only in production — this is a placeholder
    status = (request.get_json() or {}).get("kyc_status")
    if not status:
        return jsonify({"error": "missing_kyc_status"}), 400
    u = User.query.get_or_404(user_id)
    u.kyc_status = status
    db.session.commit()
    return jsonify({"status": "updated", "kyc_status": u.kyc_status})