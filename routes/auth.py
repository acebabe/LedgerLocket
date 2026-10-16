from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from models import db, User, EmailVerification, PasswordReset, RefreshToken
from utils.email import send_verification_email, send_password_reset_email
from app_factory import limiter

LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW_MINUTES = 15

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "already registered"}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = str(user.id) + '-' + str(int(datetime.utcnow().timestamp()))
    verification = EmailVerification(user_id=user.id, token=token, expires_at=datetime.utcnow() + timedelta(hours=24))
    db.session.add(verification)
    db.session.commit()

    send_verification_email(user.email, token)

    access = create_access_token(identity=user.id)
    return jsonify({"access_token": access, "user": {"id": user.id, "email": user.email}}), 201


@bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()

    # check lockout
    if user and user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"msg": "account locked, try later"}), 403

    if not user or not user.check_password(password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_WINDOW_MINUTES)
            db.session.commit()
        return jsonify({"msg": "bad credentials"}), 401

    # reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    access = create_access_token(identity=user.id)
    return jsonify({"access_token": access})


@bp.route("/verify", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"msg": "token required"}), 400
    verification = EmailVerification.query.filter_by(token=token).first()
    if not verification or verification.expires_at < datetime.utcnow():
        return jsonify({"msg": "invalid token"}), 404
    user = User.query.get(verification.user_id)
    roles = list(user.roles or [])
    if "verified" not in roles:
        roles.append("verified")
    user.roles = roles
    db.session.delete(verification)
    db.session.commit()
    return jsonify({"msg": "email verified"})


@bp.route("/password-reset/request", methods=["POST"])
@limiter.limit("5 per hour")
def request_reset():
    data = request.get_json() or {}
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "ok"})
    token = f"reset-{user.id}-{int(datetime.utcnow().timestamp())}"
    reset = PasswordReset(user_id=user.id, token=token, expires_at=datetime.utcnow() + timedelta(hours=2))
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
    if not reset or reset.expires_at < datetime.utcnow():
        return jsonify({"msg": "invalid token"}), 400
    user = User.query.get(reset.user_id)
    user.set_password(password)
    db.session.delete(reset)
    db.session.commit()
    return jsonify({"msg": "password updated"})


@bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    token = data.get("refresh")
    rt = RefreshToken.query.filter_by(token=token, revoked=False).first()
    if not rt or rt.expires_at < datetime.utcnow():
        return jsonify({"msg": "invalid or expired refresh token"}), 401
    access = create_access_token(identity=rt.user_id)
    # revoke old refresh token and issue a new one
    rt.revoked = True
    db.session.commit()
    new_token = RefreshToken(user_id=rt.user_id, token=str(uuid4()), revoked=False, expires_at=datetime.utcnow() + timedelta(days=14))
    db.session.add(new_token)
    db.session.commit()
    return jsonify({"access_token": access, "refresh": new_token.token})
