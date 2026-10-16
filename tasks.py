from celery import Celery

from config import Config

cel = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)


@cel.task
def send_notification_task(notif_id):
    from app import create_app, socketio
    from models import Notification, db

    flask_app = create_app()
    with flask_app.app_context():
        n = Notification.query.get(notif_id)
        if not n:
            return
        payload = {
            "type": n.type,
            "payload": n.payload,
            "wallet": n.wallet_address,
            "created_at": str(n.created_at),
        }
        socketio.emit("wallet_notification", payload, room=f"wallet:{n.wallet_address}")
        n.delivered = True
        db.session.commit()


def queue_notification(notif_id):
    send_notification_task.delay(notif_id)
