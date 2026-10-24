import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.job import JobListing, SavedJob, MatchResult
from backend.app.models.profile import CandidateProfile, CandidateSkill, Project, WorkExperience
from backend.app.models.assessment import JobAssessment, RiskSignal
from backend.app.api.deps import get_current_user, get_optional_current_user
from backend.app.services.url_fetcher import fetch_job_url_safely
from backend.app.services.risk_engine import analyze_job_listing
from backend.app.services.matching_engine import compute_job_match
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/jobs", tags=["Job Discovery & Matching"])

class JobSubmitRequest(BaseModel):
    title: str
    employer: str
    description: str
    employer_domain: Optional[str] = ""
    location: Optional[str] = "Remote"
    work_arrangement: Optional[str] = "remote"
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    salary_text: Optional[str] = ""
    contact_email: Optional[str] = ""
    contact_messaging: Optional[str] = ""
    application_url: Optional[str] = ""

class URLRetrieveRequest(BaseModel):
    url: str

class SaveJobRequest(BaseModel):
    status: str = "saved"  # saved or dismissed
    notes: Optional[str] = ""

@router.get("/")
async def list_jobs(
    q: Optional[str] = Query(None, description="Search term for title, employer, skill"),
    work_arrangement: Optional[str] = Query(None),
    min_match: Optional[float] = Query(None),
    sort: Optional[str] = Query("match", description="match, recent, or salary"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(JobListing).where(JobListing.is_active == True)
    
    if work_arrangement and work_arrangement.lower() != "all":
        query = query.where(JobListing.work_arrangement == work_arrangement.lower())
        
    res = await db.execute(query.order_by(JobListing.created_at.desc()))
    all_jobs = res.scalars().all()

    # Load candidate profile if logged in
    candidate_skills = []
    candidate_projects = []
    candidate_exp = []
    cand_pref = "remote"

    if current_user:
        prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
        profile = prof_res.scalar_one_or_none()
        if profile:
            cand_pref = profile.work_arrangement or "remote"
            skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
            candidate_skills = [{"canonical_name": s.canonical_name, "proficiency_level": s.proficiency_level, "verified_status": s.verified_status} for s in skills_res.scalars().all()]
            
            proj_res = await db.execute(select(Project).where(Project.profile_id == profile.id))
            candidate_projects = [{"title": p.title, "skills_used": p.skills_used} for p in proj_res.scalars().all()]

    job_results = []
    for j in all_jobs:
        req_skills = json.loads(j.required_skills) if j.required_skills else []
        pref_skills = json.loads(j.preferred_skills) if j.preferred_skills else []
        
        # Filter by search term q
        if q:
            term = q.lower()
            text_search = f"{j.title} {j.employer} {j.description} {' '.join(req_skills)}".lower()
            if term not in text_search:
                continue

        # Match calculation
        if candidate_skills:
            match_data = compute_job_match(
                candidate_skills=candidate_skills,
                candidate_projects=candidate_projects,
                candidate_experience=candidate_exp,
                required_skills=req_skills,
                preferred_skills=pref_skills,
                work_arrangement=j.work_arrangement or "remote",
                candidate_arrangement_pref=cand_pref
            )
            match_score = match_data["match_score"]
            explanation = match_data["explanation"]
        else:
            match_score = 75.0
            explanation = {"summary": "Log in or complete your profile to view personalized evidence matching."}

        if min_match and match_score < min_match:
            continue

        # Check latest risk assessment
        assess_res = await db.execute(select(JobAssessment).where(JobAssessment.job_id == j.id).order_by(JobAssessment.assessed_at.desc()))
        latest_assess = assess_res.scalar_one_or_none()

        job_results.append({
            "id": j.id,
            "title": j.title,
            "employer": j.employer,
            "employer_domain": j.employer_domain,
            "location": j.location,
            "work_arrangement": j.work_arrangement,
            "salary_text": j.salary_text,
            "description": j.description[:260] + "..." if len(j.description) > 260 else j.description,
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "match_score": match_score,
            "explanation": explanation,
            "risk_tier": latest_assess.risk_tier if latest_assess else "Lower observed risk",
            "source": j.source,
            "created_at": j.created_at.isoformat() if j.created_at else None
        })

    if sort == "match":
        job_results.sort(key=lambda x: x["match_score"], reverse=True)

    return job_results

@router.post("/")
async def create_job(
    req: JobSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Auto-extract skills if empty
    req_skills = req.required_skills or []
    if not req_skills:
        for kw in ["Python", "React", "SQL", "FastAPI", "TypeScript", "Docker", "Node.js", "PostgreSQL"]:
            if kw.lower() in req.description.lower():
                req_skills.append(kw)

    job = JobListing(
        title=req.title,
        employer=req.employer,
        employer_domain=req.employer_domain or "",
        location=req.location or "Remote",
        work_arrangement=req.work_arrangement or "remote",
        description=req.description,
        required_skills=json.dumps(req_skills),
        preferred_skills=json.dumps(req.preferred_skills or []),
        salary_text=req.salary_text or "",
        contact_email=req.contact_email or "",
        contact_messaging=req.contact_messaging or "",
        application_url=req.application_url or "",
        source="user_submitted"
    )
    db.add(job)
    await db.flush()

    # Automatically trigger initial risk assessment
    analysis = analyze_job_listing(
        title=job.title,
        employer=job.employer,
        description=job.description,
        employer_domain=job.employer_domain,
        contact_email=job.contact_email,
        contact_messaging=job.contact_messaging,
        salary_text=job.salary_text,
        application_url=job.application_url
    )
    assessment = JobAssessment(
        job_id=job.id,
        user_id=current_user.id,
        risk_score=analysis["risk_score"],
        risk_tier=analysis["risk_tier"],
        summary=analysis["summary"],
        positive_signals=json.dumps(analysis["positive_signals"]),
        unknown_signals=json.dumps(analysis["unknown_signals"])
    )
    db.add(assessment)
    await db.flush()

    for s in analysis["signals"]:
        sig = RiskSignal(
            assessment_id=assessment.id,
            signal_category=s["signal_category"],
            severity=s["severity"],
            title=s["title"],
            description=s["description"],
            evidence_excerpt=s["evidence_excerpt"],
            certainty=s["certainty"],
            recommended_action=s["recommended_action"]
        )
        db.add(sig)

    await db.commit()
    await db.refresh(job)
    
    await log_audit_event(db, current_user.id, "job_submitted", {"job_id": job.id, "title": job.title})
    return {"message": "Job listing submitted and evaluated", "id": job.id, "assessment": analysis}

@router.post("/retrieve-url")
async def retrieve_job_url(
    req: URLRetrieveRequest,
    current_user: User = Depends(get_current_user)
):
    result = await fetch_job_url_safely(req.url)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return {
        "url": result["url"],
        "title": result["title"],
        "extracted_content": result["content"]
    }

@router.get("/saved/all")
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(SavedJob, JobListing)
        .join(JobListing, SavedJob.job_id == JobListing.id)
        .where(SavedJob.user_id == current_user.id, SavedJob.status == "saved")
        .order_by(SavedJob.created_at.desc())
    )
    records = res.all()
    return [
        {
            "saved_id": s.id,
            "job_id": j.id,
            "title": j.title,
            "employer": j.employer,
            "location": j.location,
            "work_arrangement": j.work_arrangement,
            "salary_text": j.salary_text,
            "required_skills": json.loads(j.required_skills) if j.required_skills else [],
            "notes": s.notes,
            "saved_at": s.created_at.isoformat() if s.created_at else None
        } for s, j in records
    ]

@router.post("/{job_id}/save")
async def save_or_dismiss_job(
    job_id: str,
    req: SaveJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(SavedJob).where(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id))
    existing = res.scalar_one_or_none()
    
    if existing:
        existing.status = req.status
        existing.notes = req.notes or existing.notes
    else:
        saved = SavedJob(
            user_id=current_user.id,
            job_id=job_id,
            status=req.status,
            notes=req.notes or ""
        )
        db.add(saved)
        
    await db.commit()
    return {"message": f"Job marked as {req.status}"}

@router.get("/{job_id}")
async def get_job_detail(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    j_res = await db.execute(select(JobListing).where(JobListing.id == job_id))
    job = j_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    req_skills = json.loads(job.required_skills) if job.required_skills else []
    pref_skills = json.loads(job.preferred_skills) if job.preferred_skills else []

    # Get latest assessment
    assess_res = await db.execute(select(JobAssessment).where(JobAssessment.job_id == job.id).order_by(JobAssessment.assessed_at.desc()))
    assessment = assess_res.scalar_one_or_none()
    
    signals_data = []
    positive_signals = []
    unknown_signals = []
    if assessment:
        sig_res = await db.execute(select(RiskSignal).where(RiskSignal.assessment_id == assessment.id))
        signals_data = [
            {
                "signal_category": s.signal_category,
                "severity": s.severity,
                "title": s.title,
                "description": s.description,
                "evidence_excerpt": s.evidence_excerpt,
                "certainty": s.certainty,
                "recommended_action": s.recommended_action
            } for s in sig_res.scalars().all()
        ]
        try:
            positive_signals = json.loads(assessment.positive_signals) if assessment.positive_signals else []
            unknown_signals = json.loads(assessment.unknown_signals) if assessment.unknown_signals else []
        except Exception:
            pass

    # Compute personalized matching if logged in
    match_info = None
    if current_user:
        prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
        profile = prof_res.scalar_one_or_none()
        if profile:
            skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
            cand_skills = [{"canonical_name": s.canonical_name, "proficiency_level": s.proficiency_level, "verified_status": s.verified_status} for s in skills_res.scalars().all()]
            proj_res = await db.execute(select(Project).where(Project.profile_id == profile.id))
            cand_projects = [{"title": p.title, "skills_used": p.skills_used} for p in proj_res.scalars().all()]
            
            match_data = compute_job_match(
                candidate_skills=cand_skills,
                candidate_projects=cand_projects,
                candidate_experience=[],
                required_skills=req_skills,
                preferred_skills=pref_skills,
                work_arrangement=job.work_arrangement or "remote",
                candidate_arrangement_pref=profile.work_arrangement or "remote"
            )
            match_info = match_data

    return {
        "id": job.id,
        "title": job.title,
        "employer": job.employer,
        "employer_domain": job.employer_domain,
        "location": job.location,
        "work_arrangement": job.work_arrangement,
        "salary_text": job.salary_text,
        "description": job.description,
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "contact_email": job.contact_email,
        "contact_messaging": job.contact_messaging,
        "application_url": job.application_url,
        "source": job.source,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "assessment": {
            "risk_score": assessment.risk_score if assessment else 12.0,
            "risk_tier": assessment.risk_tier if assessment else "Lower observed risk",
            "summary": assessment.summary if assessment else "Standard professional recruitment patterns detected.",
            "signals": signals_data,
            "positive_signals": positive_signals,
            "unknown_signals": unknown_signals,
            "method": assessment.method if assessment else "Multi-Signal Evaluation"
        },
        "match": match_info
    }
