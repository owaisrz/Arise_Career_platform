from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.job import JobListing
from backend.app.models.report import JobReport
from backend.app.api.deps import get_current_user
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/reports", tags=["Listing Reports"])

class SubmitReportRequest(BaseModel):
    job_id: str
    reason: str  # scam_payment, fake_company, misleading_info, harassment, other
    details: Optional[str] = ""

@router.post("/")
async def report_job_listing(
    req: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    j_res = await db.execute(select(JobListing).where(JobListing.id == req.job_id))
    job = j_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    report = JobReport(
        job_id=req.job_id,
        user_id=current_user.id,
        reason=req.reason,
        details=req.details or "",
        status="pending_review"
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    await log_audit_event(db, current_user.id, "job_reported", {
        "job_id": req.job_id,
        "reason": req.reason,
        "report_id": report.id
    })

    return {
        "message": "Report submitted successfully. Allegations are subject to independent administrative review before disciplinary action.",
        "report_id": report.id,
        "status": "pending_review"
    }

@router.get("/mine")
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(JobReport, JobListing)
        .join(JobListing, JobReport.job_id == JobListing.id)
        .where(JobReport.user_id == current_user.id)
        .order_by(JobReport.reported_at.desc())
    )
    items = res.all()
    return [
        {
            "id": r.id,
            "job_id": j.id,
            "job_title": j.title,
            "employer": j.employer,
            "reason": r.reason,
            "details": r.details,
            "status": r.status,
            "reported_at": r.reported_at.isoformat() if r.reported_at else None
        } for r, j in items
    ]
