from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, EmailVerification, PasswordReset, RefreshToken
from utils.email import send_verification_email, send_password_reset_email

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "already registered"}), 400

    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    token = user.id
    verification = EmailVerification(user_id=user.id, token=str(token), expires_at=__import__('datetime').datetime.utcnow())
    # keep simple token for demo
    db.session.add(verification)
    db.session.commit()

    access = create_access_token(identity=user.id)
    return jsonify({"access_token": access, "user": {"id": user.id, "email": user.email}}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "bad credentials"}), 401
    access = create_access_token(identity=user.id)
    return jsonify({"access_token": access})


@bp.route("/verify", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"msg": "token required"}), 400
    verification = EmailVerification.query.filter_by(token=token).first()
    if not verification:
        return jsonify({"msg": "invalid token"}), 404
    user = User.query.get(verification.user_id)
    user.roles = list(user.roles or [])
    if "verified" not in user.roles:
        user.roles.append("verified")
    db.session.delete(verification)
    db.session.commit()
    return jsonify({"msg": "email verified"})


@bp.route("/password-reset/request", methods=["POST"])
def request_reset():
    data = request.get_json() or {}
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "ok"})
    token = f"reset-{user.id}-{user.email}"
    reset = PasswordReset(user_id=user.id, token=token, expires_at=__import__('datetime').datetime.utcnow())
    db.session.add(reset)
    db.session.commit()
    send_password_reset_email(user.email, token)
    return jsonify({"msg": "ok"})


@bp.route("/password-reset/confirm", methods=["POST"])
def confirm_reset():
    data = request.get_json() or {}
    token = data.get("token")
    password = data.get("password")
    if not token or not password:
        return jsonify({"msg": "token and password required"}), 400
    reset = PasswordReset.query.filter_by(token=token).first()
    if not reset:
        return jsonify({"msg": "invalid token"}), 400
    user = User.query.get(reset.user_id)
    user.password_hash = generate_password_hash(password)
    db.session.delete(reset)
    db.session.commit()
    return jsonify({"msg": "password updated"})


@bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    token = data.get("refresh")
    rt = RefreshToken.query.filter_by(token=token, revoked=False).first()
    if not rt:
        return jsonify({"msg": "invalid refresh token"}), 401
    access = create_access_token(identity=rt.user_id)
    return jsonify({"access_token": access})
