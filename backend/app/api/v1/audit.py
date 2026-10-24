import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.report import AuditEvent
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("/history")
async def get_audit_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(AuditEvent).where(AuditEvent.user_id == current_user.id).order_by(AuditEvent.created_at.desc()).limit(50)
    )
    events = res.scalars().all()
    
    formatted = []
    for e in events:
        try:
            details = json.loads(e.details_json) if e.details_json else {}
        except Exception:
            details = {}
        formatted.append({
            "id": e.id,
            "event_type": e.event_type,
            "details": details,
            "ip_address": e.ip_address,
            "created_at": e.created_at.isoformat() if e.created_at else None
        })
        
    return formatted
