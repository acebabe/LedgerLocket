from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, User

bp = Blueprint("admin", __name__)


def admin_required(func):
    def wrapper(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity
n        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or "admin" not in (user.roles or []):
            return jsonify({"msg": "admin required"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "email": u.email, "roles": u.roles or []} for u in users])


@bp.route("/set-role", methods=["POST"])
@jwt_required()
@admin_required
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
