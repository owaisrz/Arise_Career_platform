import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import (
    CandidateProfile,
    Education,
    WorkExperience,
    Project,
    CandidateSkill,
    SkillEvidence
)
from backend.app.models.document import ExtractedClaim
from backend.app.api.deps import get_current_user
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])

class ProfileUpdateRequest(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    preferred_role: Optional[str] = None
    preferred_location: Optional[str] = None
    work_arrangement: Optional[str] = None
    availability: Optional[str] = None
    phone: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class SkillCreateRequest(BaseModel):
    skill_name: str
    proficiency_level: str = "Intermediate"
    category: str = "Technical"

class ProjectCreateRequest(BaseModel):
    title: str
    description: str
    skills_used: List[str]
    demo_url: Optional[str] = ""
    repo_url: Optional[str] = ""
    role: Optional[str] = "Lead Developer"

class EducationCreateRequest(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = ""
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = ""

class ExperienceCreateRequest(BaseModel):
    company: str
    role: str
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    is_current: Optional[bool] = False
    description: Optional[str] = ""

class ClaimActionRequest(BaseModel):
    claim_id: str
    action: str  # approve or reject
    user_correction: Optional[str] = None

@router.get("/")
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    edu_res = await db.execute(select(Education).where(Education.profile_id == profile.id))
    education = edu_res.scalars().all()

    exp_res = await db.execute(select(WorkExperience).where(WorkExperience.profile_id == profile.id))
    experience = exp_res.scalars().all()

    proj_res = await db.execute(select(Project).where(Project.profile_id == profile.id))
    projects = proj_res.scalars().all()

    skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
    skills = skills_res.scalars().all()

    # Calculate truthful completeness percentage
    checks = [
        bool(profile.headline),
        bool(profile.summary),
        bool(profile.preferred_role),
        bool(profile.phone or profile.github_url or profile.portfolio_url),
        len(education) > 0,
        len(projects) > 0,
        len(skills) > 0,
        len(experience) > 0,
    ]
    completeness = round((sum(1 for c in checks if c) / len(checks)) * 100)

    # Format projects with parsed skills
    formatted_projects = []
    for p in projects:
        try:
            p_skills = json.loads(p.skills_used)
        except Exception:
            p_skills = [s.strip() for s in p.skills_used.split(",") if s.strip()]
        formatted_projects.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "skills_used": p_skills,
            "demo_url": p.demo_url,
            "repo_url": p.repo_url,
            "role": p.role,
            "is_extracted": p.is_extracted,
            "source_reference": p.source_reference
        })

    return {
        "id": profile.id,
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "headline": profile.headline,
        "summary": profile.summary,
        "preferred_role": profile.preferred_role,
        "preferred_location": profile.preferred_location,
        "work_arrangement": profile.work_arrangement,
        "availability": profile.availability,
        "phone": profile.phone,
        "portfolio_url": profile.portfolio_url,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "completeness_percentage": completeness,
        "education": [
            {
                "id": e.id,
                "institution": e.institution,
                "degree": e.degree,
                "field_of_study": e.field_of_study,
                "start_year": e.start_year,
                "end_year": e.end_year,
                "grade": e.grade,
                "is_extracted": e.is_extracted,
                "source_reference": e.source_reference
            } for e in education
        ],
        "work_experience": [
            {
                "id": w.id,
                "company": w.company,
                "role": w.role,
                "location": w.location,
                "start_date": w.start_date,
                "end_date": w.end_date,
                "is_current": w.is_current,
                "description": w.description,
                "is_extracted": w.is_extracted,
                "source_reference": w.source_reference
            } for w in experience
        ],
        "projects": formatted_projects,
        "skills": [
            {
                "id": s.id,
                "skill_name": s.skill_name,
                "canonical_name": s.canonical_name,
                "proficiency_level": s.proficiency_level,
                "category": s.category,
                "verified_status": s.verified_status,
                "confidence_score": s.confidence_score
            } for s in skills
        ]
    }

@router.put("/")
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        
    for field, val in req.dict(exclude_unset=True).items():
        setattr(profile, field, val)
        
    await db.commit()
    await log_audit_event(db, current_user.id, "profile_edit", req.dict(exclude_unset=True))
    return {"message": "Profile updated successfully"}

@router.post("/skills")
async def add_skill(
    req: SkillCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    skill = CandidateSkill(
        profile_id=profile.id,
        skill_name=req.skill_name,
        canonical_name=req.skill_name,
        proficiency_level=req.proficiency_level,
        category=req.category,
        verified_status="self_reported",
        confidence_score=0.75
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return {"message": "Skill added", "id": skill.id}

@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    await db.execute(delete(CandidateSkill).where(CandidateSkill.id == skill_id, CandidateSkill.profile_id == profile.id))
    await db.commit()
    return {"message": "Skill deleted"}

@router.post("/projects")
async def add_project(
    req: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    project = Project(
        profile_id=profile.id,
        title=req.title,
        description=req.description,
        skills_used=json.dumps(req.skills_used),
        demo_url=req.demo_url or "",
        repo_url=req.repo_url or "",
        role=req.role or "Lead Developer"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Also elevate verified status of skills used in project
    for sk in req.skills_used:
        res = await db.execute(
            select(CandidateSkill).where(
                CandidateSkill.profile_id == profile.id,
                CandidateSkill.canonical_name.ilike(sk)
            )
        )
        existing = res.scalar_one_or_none()
        if existing:
            existing.verified_status = "project_verified"
            existing.confidence_score = 0.95
    await db.commit()
    
    await log_audit_event(db, current_user.id, "project_added", {"title": req.title})
    return {"message": "Project created and linked", "id": project.id}

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    await db.execute(delete(Project).where(Project.id == project_id, Project.profile_id == profile.id))
    await db.commit()
    return {"message": "Project removed"}

@router.post("/claims/action")
async def process_claim_action(
    req: ClaimActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    claim_res = await db.execute(select(ExtractedClaim).where(ExtractedClaim.id == req.claim_id))
    claim = claim_res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Extracted claim not found")
        
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()

    if req.action == "approve":
        claim.status = "approved"
        # Merge into profile
        if claim.claim_type == "skill":
            # Add to skills
            new_skill = CandidateSkill(
                profile_id=profile.id,
                skill_name=claim.raw_value,
                canonical_name=claim.normalized_value or claim.raw_value,
                proficiency_level="Intermediate",
                category="Technical",
                verified_status="document_extracted",
                confidence_score=claim.confidence
            )
            db.add(new_skill)
            await db.flush()
            # Add evidence pointer
            evidence = SkillEvidence(
                candidate_skill_id=new_skill.id,
                evidence_type="document_claim",
                source_title="Document Extraction",
                excerpt=claim.text_excerpt,
                page_number=claim.page_number,
                confidence=claim.confidence,
                is_approved=True
            )
            db.add(evidence)
        elif claim.claim_type == "education":
            edu = Education(
                profile_id=profile.id,
                institution="Institution (Extracted)",
                degree=claim.raw_value,
                is_extracted=True,
                source_reference=f"Page {claim.page_number}: {claim.text_excerpt}"
            )
            db.add(edu)
        elif claim.claim_type == "personal_info":
            if claim.field_name == "phone":
                profile.phone = claim.raw_value
            elif claim.field_name == "github":
                profile.github_url = claim.raw_value
            elif claim.field_name == "linkedin":
                profile.linkedin_url = claim.raw_value

        await log_audit_event(db, current_user.id, "evidence_approved", {"claim_id": claim.id, "claim_type": claim.claim_type, "value": claim.raw_value})
    else:
        claim.status = "rejected"
        await log_audit_event(db, current_user.id, "evidence_rejected", {"claim_id": claim.id, "claim_type": claim.claim_type})

    await db.commit()
    return {"message": f"Claim {req.action}d successfully"}
