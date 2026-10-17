from . import blueprint
from flask import request, jsonify
from app.models.user import User


def _is_admin_header():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return False
    user = User.query.get(int(user_id))
    return bool(user and user.is_admin)


@blueprint.route("/admin/users", methods=["GET"])
def list_users():
    if not _is_admin_header():
        return jsonify({"error": "forbidden"}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        "id": u.id,
        "email": u.email,
        "is_admin": u.is_admin,
        "kyc_status": u.kyc_status,
    } for u in users])
