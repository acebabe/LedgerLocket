from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, db

bp = Blueprint("admin", __name__)


@bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "email": u.email, "roles": u.roles or []} for u in users])


@bp.route("/set-role", methods=["POST"])
def set_role():
    data = request.get_json() or {}
    email = data.get("email")
    role = data.get("role")
    if not email or not role:
        return jsonify({"msg": "email and role required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "user not found"}), 404
    roles = list(user.roles or [])
    if role not in roles:
        roles.append(role)
    user.roles = roles
    db.session.commit()
    return jsonify({"msg": "updated"})
