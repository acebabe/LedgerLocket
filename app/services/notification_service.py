# app/services/notification_service.py
from flask_mail import Message
from app.extensions import mail, db
from app.models.notification import Notification
from threading import Thread


def _send_async(app, msg):
    with app.app_context():
        mail.send(msg)


class NotificationService:
    def __init__(self, app):
        self.app = app

    def notify_address(self, address, message, tx_id=None, email=None):
        n = Notification(address=address, message=message, email=email)
        db.session.add(n)
        db.session.commit()

        if email and self.app.config.get('MAIL_USERNAME'):
            msg = Message(
                subject='LedgerLocket: Incoming Test Credit',
                recipients=[email],
                body=f"{message}\nTransaction: {tx_id}"
            )
            thr = Thread(target=_send_async, args=(self.app, msg))
            thr.start()
