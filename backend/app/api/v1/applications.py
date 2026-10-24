from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.job import JobListing
from backend.app.models.application import Application, ApplicationNote
from backend.app.api.deps import get_current_user
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/applications", tags=["Application Pipeline"])

class CreateApplicationRequest(BaseModel):
    job_id: str
    stage: Optional[str] = "Saved"
    notes: Optional[str] = ""
    resume_version_id: Optional[str] = None

class UpdateStageRequest(BaseModel):
    stage: str  # Saved, Planned, Applied, Assessment, Interview, Offer, Rejected, Withdrawn

class UpdateApplicationDetailsRequest(BaseModel):
    applied_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    interview_date: Optional[str] = None
    notes: Optional[str] = None
    outcome_notes: Optional[str] = None
    resume_version_id: Optional[str] = None

class AddNoteRequest(BaseModel):
    content: str

@router.get("/")
async def list_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Application, JobListing)
        .join(JobListing, Application.job_id == JobListing.id)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
    )
    records = res.all()

    pipeline_stages = ["Saved", "Planned", "Applied", "Assessment", "Interview", "Offer", "Rejected", "Withdrawn"]
    grouped = {stage: [] for stage in pipeline_stages}

    for app, job in records:
        entry = {
            "id": app.id,
            "job_id": job.id,
            "title": job.title,
            "employer": job.employer,
            "location": job.location,
            "work_arrangement": job.work_arrangement,
            "stage": app.stage,
            "applied_date": app.applied_date,
            "follow_up_date": app.follow_up_date,
            "interview_date": app.interview_date,
            "notes": app.notes,
            "outcome_notes": app.outcome_notes,
            "resume_version_id": app.resume_version_id,
            "created_at": app.created_at.isoformat() if app.created_at else None
        }
        if app.stage in grouped:
            grouped[app.stage].append(entry)
        else:
            grouped["Saved"].append(entry)

    total_active = sum(len(grouped[s]) for s in ["Applied", "Assessment", "Interview"])

    return {
        "pipeline": grouped,
        "total_applications": len(records),
        "total_active": total_active
    }

@router.post("/")
async def create_application(
    req: CreateApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify job exists
    j_res = await db.execute(select(JobListing).where(JobListing.id == req.job_id))
    job = j_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    # Check if application already exists
    existing_res = await db.execute(select(Application).where(Application.user_id == current_user.id, Application.job_id == req.job_id))
    existing = existing_res.scalar_one_or_none()
    if existing:
        return {"message": "Application already exists in pipeline", "id": existing.id}

    app = Application(
        user_id=current_user.id,
        job_id=req.job_id,
        stage=req.stage or "Saved",
        notes=req.notes or "",
        resume_version_id=req.resume_version_id
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)

    await log_audit_event(db, current_user.id, "application_created", {
        "application_id": app.id,
        "job_title": job.title,
        "employer": job.employer,
        "stage": app.stage
    })

    return {"message": "Application added to pipeline", "id": app.id}

@router.put("/{app_id}/stage")
async def update_application_stage(
    app_id: str,
    req: UpdateStageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    app_res = await db.execute(select(Application).where(Application.id == app_id, Application.user_id == current_user.id))
    app = app_res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_stage = app.stage
    app.stage = req.stage
    await db.commit()

    await log_audit_event(db, current_user.id, "application_stage_change", {
        "application_id": app.id,
        "old_stage": old_stage,
        "new_stage": req.stage
    })

    return {"message": f"Application stage transitioned from {old_stage} to {req.stage}"}

@router.put("/{app_id}")
async def update_application_details(
    app_id: str,
    req: UpdateApplicationDetailsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    app_res = await db.execute(select(Application).where(Application.id == app_id, Application.user_id == current_user.id))
    app = app_res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, val in req.dict(exclude_unset=True).items():
        if val is not None:
            setattr(app, field, val)

    await db.commit()
    return {"message": "Application details updated"}

@router.delete("/{app_id}")
async def delete_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    app_res = await db.execute(select(Application).where(Application.id == app_id, Application.user_id == current_user.id))
    app = app_res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.execute(delete(ApplicationNote).where(ApplicationNote.application_id == app.id))
    await db.execute(delete(Application).where(Application.id == app.id))
    await db.commit()

    return {"message": "Application removed from pipeline"}
