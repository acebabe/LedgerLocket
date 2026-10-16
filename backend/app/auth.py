from flask import Blueprint, request, jsonify, current_app
from .extensions import db
from .models import User, Wallet, Transaction, AuditLog, RefreshToken
from datetime import datetime, timedelta
import uuid, os
import jwt
from werkzeug.security import gen_salt

bp = Blueprint('auth', __name__)

JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret')
ACCESS_EXPIRES = int(os.getenv('ACCESS_EXPIRES', '900'))  # seconds
REFRESH_EXPIRES = int(os.getenv('REFRESH_EXPIRES', '1209600'))  # 14 days


def _generate_tokens(user_id):
    now = datetime.utcnow()
    access_payload = {
        'sub': user_id,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(seconds=ACCESS_EXPIRES)).timestamp())
    }
    access = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')

    refresh_token = gen_salt(40)
    rt = RefreshToken(token=refresh_token, user_id=user_id, expires_at=(now + timedelta(seconds=REFRESH_EXPIRES)))
    db.session.add(rt)
    db.session.commit()

    return access, refresh_token

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error':'missing fields'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'user exists'}), 400
    u = User(email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    # TODO: send verification email
    access, refresh = _generate_tokens(u.id)
    return jsonify({'access':access, 'refresh':refresh}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify({'error':'invalid credentials'}), 401
    access, refresh = _generate_tokens(u.id)
    return jsonify({'access':access, 'refresh':refresh})

@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json() or {}
    token = data.get('refresh')
    if not token:
        return jsonify({'error':'missing refresh token'}), 400
    rt = RefreshToken.query.filter_by(token=token, revoked=False).first()
    if not rt or rt.expires_at < datetime.utcnow():
        return jsonify({'error':'invalid refresh token'}), 401
    access, refresh = _generate_tokens(rt.user_id)
    # revoke previous refresh
    rt.revoked = True
    db.session.commit()
    return jsonify({'access':access, 'refresh':refresh})
