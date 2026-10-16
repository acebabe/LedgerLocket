from flask import Flask
from flask_jwt_extended import get_jwt_identity, jwt_required

from app_factory import create_app
from models import User, Wallet, db, Notification

app = create_app()


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/admin/users")
@jwt_required()
def admin_users():
    current_id = get_jwt_identity()
    user = User.query.get(current_id)
    if not user or "admin" not in (user.roles or []):
        return {"msg": "admin required"}, 403
    return {"users": [{"id": u.id, "email": u.email, "roles": u.roles or []} for u in User.query.all()]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
