
from app.models.audit_event import AuditEvent
def record_event(db, actor: str, event_type: str, details: str = ""):
    db.add(AuditEvent(actor=actor, event_type=event_type, details=details))
    db.commit()
