from . import blueprint
from flask import jsonify
from app.models.notification import Notification


@blueprint.route("/notifications", methods=["GET"])
def list_notifications():
    items = Notification.query.order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([{ 
        "id": n.id,
        "address": n.address,
        "message": n.message,
        "read": n.read,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    } for n in items])
