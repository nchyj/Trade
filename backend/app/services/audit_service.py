from ..db import SessionLocal
from ..models import AuditLog


def log_event(module: str, action: str, detail: str):
    session = SessionLocal()
    try:
        session.add(AuditLog(module=module, action=action, detail=detail))
        session.commit()
    finally:
        session.close()
