from app.extensions import db
from app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def record(actor, action, payload=None):
        a = AuditLog(actor=actor, action=action, payload=payload)
        db.session.add(a)
        db.session.commit()
        return a
