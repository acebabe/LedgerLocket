from celery import Celery
from config import Config
from models import db, Notification, Wallet
from app import create_app, socketio
import json
import os

cel = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)
flask_app = create_app()
cel.conf.update(flask_app.config)

@cel.task
def send_notification_task(notif_id):
    with flask_app.app_context():
        n = Notification.query.get(notif_id)
        if n is None: 
            return
        # Example: push via websocket to connected clients listening for wallet address
        payload = {"type": n.type, "payload": n.payload, "wallet": n.wallet_address, "created_at": str(n.created_at)}
        # Emit with Socket.IO channel: wallet:<address>
        socketio.emit("wallet_notification", payload, room=f"wallet:{n.wallet_address}")
        # TODO: send email/push using 3rd-party providers (SendGrid, Twilio, FCM)
        n.delivered = True
        db.session.commit()

def queue_notification(notif_id):
    send_notification_task.delay(notif_id)