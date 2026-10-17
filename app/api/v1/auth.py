from . import blueprint
from flask import request, jsonify, current_app
from app.extensions import db
from app.models.user import User
import bcrypt


@blueprint.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error':'missing_credentials'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'already_exists'}), 400
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status':'created', 'user_id': user.id}), 201


@blueprint.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error':'invalid_credentials'}), 401
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({'error':'invalid_credentials'}), 401
    # simple session token (for demo only)
    token = f"token-{user.id}"
    return jsonify({'status':'ok', 'token': token, 'user_id': user.id})
