from . import blueprint
from flask import request, jsonify
from app.extensions import db
from app.models.user import User
import bcrypt
from app.utils.jwt_auth import create_token


@blueprint.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "missing_credentials"}), 400
    if len(password) < 8:
        return jsonify({"error": "password_too_short"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "already_exists"}), 400

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "created", "user_id": user.id}), 201


@blueprint.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "invalid_credentials"}), 401

    token = create_token(user.id)
    return jsonify({
        "status": "ok",
        "token": token,
        "user_id": user.id,
        "is_admin": bool(user.is_admin),
        "kyc_status": user.kyc_status,
    })
