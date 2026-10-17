import jwt
from datetime import datetime, timedelta
from flask import current_app

ALGO = "HS256"

def create_token(user_id, expires_seconds=3600):
    secret = current_app.config.get("SECRET_KEY")
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_seconds)
    }
    return jwt.encode(payload, secret, algorithm=ALGO)

def decode_token(token):
    secret = current_app.config.get("SECRET_KEY")
    payload = jwt.decode(token, secret, algorithms=[ALGO])
    return payload.get("sub")