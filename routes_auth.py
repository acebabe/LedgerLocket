from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"msg": "email and password required"}, 400
    if User.query.filter_by(email=email).first():
        return {"msg": "already registered"}, 400
    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    access = create_access_token(identity=user.id)
    return {"access_token": access}, 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not check_password_hash(user.password_hash, data.get("password", "")):
        return {"msg": "bad credentials"}, 401
    token = create_access_token(identity=user.id)
    return {"access_token": token}