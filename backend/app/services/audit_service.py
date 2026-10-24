import json
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.report import AuditEvent

async def log_audit_event(
    db: AsyncSession,
    user_id: str,
    event_type: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1"
) -> AuditEvent:
    event = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        details_json=json.dumps(details or {}),
        ip_address=ip_address
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
