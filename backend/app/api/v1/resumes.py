import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile, CandidateSkill, Project, Education, WorkExperience
from backend.app.models.resume import ResumeDocument, EmployerSharingRecord
from backend.app.api.deps import get_current_user
from backend.app.services.resume_service import generate_tailored_resume_content
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/resumes", tags=["Resume Studio & Privacy"])

class CreateResumeVersionRequest(BaseModel):
    version_name: str
    target_job_id: Optional[str] = None
    target_employer: Optional[str] = ""
    summary: Optional[str] = None
    selected_project_ids: Optional[List[str]] = []
    selected_skills: Optional[List[str]] = []
    is_redacted: Optional[bool] = False
    redacted_fields: Optional[List[str]] = ["phone", "email"]

class ShareResumeRequest(BaseModel):
    resume_id: str
    employer_name: str
    contact_visibility: Optional[str] = "redacted"  # full, redacted, email_only

@router.get("/")
async def list_resume_versions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(ResumeDocument).where(ResumeDocument.user_id == current_user.id).order_by(ResumeDocument.created_at.desc()))
    resumes = res.scalars().all()
    
    # Also fetch active share records
    share_res = await db.execute(select(EmployerSharingRecord).where(EmployerSharingRecord.user_id == current_user.id).order_by(EmployerSharingRecord.shared_at.desc()))
    shares = share_res.scalars().all()

    return {
        "versions": [
            {
                "id": r.id,
                "version_name": r.version_name,
                "target_employer": r.target_employer,
                "target_job_id": r.target_job_id,
                "summary": r.summary,
                "is_redacted": r.is_redacted,
                "redacted_fields": json.loads(r.redacted_fields) if r.redacted_fields else [],
                "share_token": r.share_token,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in resumes
        ],
        "shared_records": [
            {
                "id": s.id,
                "resume_id": s.resume_id,
                "employer_name": s.employer_name,
                "share_token": s.share_token,
                "contact_visibility": s.contact_visibility,
                "status": s.status,
                "shared_at": s.shared_at.isoformat() if s.shared_at else None,
                "revoked_at": s.revoked_at.isoformat() if s.revoked_at else None
            } for s in shares
        ]
    }

@router.post("/generate")
async def create_resume_version(
    req: CreateResumeVersionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    resume = ResumeDocument(
        user_id=current_user.id,
        version_name=req.version_name,
        target_job_id=req.target_job_id,
        target_employer=req.target_employer or "",
        summary=req.summary or "",
        selected_projects=json.dumps(req.selected_project_ids or []),
        selected_skills=json.dumps(req.selected_skills or []),
        is_redacted=req.is_redacted or False,
        redacted_fields=json.dumps(req.redacted_fields or []),
        share_token=uuid.uuid4().hex
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    await log_audit_event(db, current_user.id, "resume_version_created", {
        "resume_id": resume.id,
        "version_name": resume.version_name,
        "target_employer": resume.target_employer,
        "is_redacted": resume.is_redacted
    })

    return {"message": "Tailored resume version created", "id": resume.id}

@router.get("/{resume_id}/content")
async def get_resume_version_content(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    r_res = await db.execute(select(ResumeDocument).where(ResumeDocument.id == resume_id, ResumeDocument.user_id == current_user.id))
    resume = r_res.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")

    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    
    edu_res = await db.execute(select(Education).where(Education.profile_id == profile.id))
    exp_res = await db.execute(select(WorkExperience).where(WorkExperience.profile_id == profile.id))
    proj_res = await db.execute(select(Project).where(Project.profile_id == profile.id))
    skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))

    profile_dict = {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": profile.phone if profile else "",
        "headline": profile.headline if profile else "",
        "summary": resume.summary or (profile.summary if profile else ""),
        "portfolio_url": profile.portfolio_url if profile else "",
        "github_url": profile.github_url if profile else "",
        "education": [{"degree": e.degree, "institution": e.institution, "start_year": e.start_year, "end_year": e.end_year} for e in edu_res.scalars().all()],
        "work_experience": [{"role": w.role, "company": w.company, "start_date": w.start_date, "end_date": w.end_date, "description": w.description} for w in exp_res.scalars().all()],
        "projects": [{"id": p.id, "title": p.title, "description": p.description, "skills_used": p.skills_used} for p in proj_res.scalars().all()],
        "skills": [{"canonical_name": s.canonical_name, "proficiency_level": s.proficiency_level, "verified_status": s.verified_status} for s in skills_res.scalars().all()]
    }

    selected_projs = json.loads(resume.selected_projects) if resume.selected_projects else []
    selected_sk = json.loads(resume.selected_skills) if resume.selected_skills else []
    redacted_f = json.loads(resume.redacted_fields) if resume.redacted_fields else []

    rendered = generate_tailored_resume_content(
        profile_data=profile_dict,
        selected_project_ids=selected_projs,
        selected_skills=selected_sk,
        is_redacted=resume.is_redacted,
        redacted_fields=redacted_f
    )

    return {
        "version_info": {
            "id": resume.id,
            "version_name": resume.version_name,
            "target_employer": resume.target_employer,
            "is_redacted": resume.is_redacted,
            "share_token": resume.share_token
        },
        "content": rendered
    }

@router.post("/share")
async def share_resume_with_employer(
    req: ShareResumeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    r_res = await db.execute(select(ResumeDocument).where(ResumeDocument.id == req.resume_id, ResumeDocument.user_id == current_user.id))
    resume = r_res.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")

    share_token = f"sh_{uuid.uuid4().hex[:12]}"
    share_record = EmployerSharingRecord(
        user_id=current_user.id,
        resume_id=resume.id,
        employer_name=req.employer_name,
        share_token=share_token,
        consent_granted=True,
        contact_visibility=req.contact_visibility or "redacted",
        status="active"
    )
    db.add(share_record)
    await db.commit()
    await db.refresh(share_record)

    await log_audit_event(db, current_user.id, "employer_share_created", {
        "employer_name": req.employer_name,
        "resume_id": resume.id,
        "contact_visibility": req.contact_visibility
    })

    return {
        "message": f"Consent-based share created for {req.employer_name}",
        "share_id": share_record.id,
        "share_token": share_token,
        "share_url": f"/shared/resume/{share_token}"
    }

@router.post("/shares/{share_id}/revoke")
async def revoke_employer_share(
    share_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    s_res = await db.execute(select(EmployerSharingRecord).where(EmployerSharingRecord.id == share_id, EmployerSharingRecord.user_id == current_user.id))
    share = s_res.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share record not found")

    share.status = "revoked"
    share.revoked_at = datetime.now(timezone.utc)
    await db.commit()

    await log_audit_event(db, current_user.id, "consent_revoked", {
        "share_id": share.id,
        "employer_name": share.employer_name
    })

    return {
        "message": f"Access for {share.employer_name} successfully revoked. Future access via this token is invalidated.",
        "notice": "Note: Revocation disables online access to the platform-hosted link; it cannot retract copies an employer may have previously saved or printed."
    }
