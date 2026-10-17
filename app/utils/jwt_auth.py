import jwt
from datetime import datetime, timedelta
from flask import current_app

ALGO = "HS256"


def create_token(user_id, expires_seconds=3600 * 24):
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_seconds),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm=ALGO)


def decode_token(token):
    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=[ALGO])
    return payload.get("sub")
