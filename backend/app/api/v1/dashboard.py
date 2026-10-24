import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile, CandidateSkill, Project, Education, WorkExperience
from backend.app.models.document import Document
from backend.app.models.job import JobListing, SavedJob
from backend.app.models.application import Application
from backend.app.models.career_plan import CareerPlan, CareerPlanTask
from backend.app.models.report import AuditEvent
from backend.app.api.deps import get_current_user
from backend.app.services.matching_engine import compute_job_match

router = APIRouter(prefix="/dashboard", tags=["Candidate Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()

    skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id if profile else None))
    skills = skills_res.scalars().all()

    proj_res = await db.execute(select(Project).where(Project.profile_id == profile.id if profile else None))
    projects = proj_res.scalars().all()

    edu_res = await db.execute(select(Education).where(Education.profile_id == profile.id if profile else None))
    education = edu_res.scalars().all()

    exp_res = await db.execute(select(WorkExperience).where(WorkExperience.profile_id == profile.id if profile else None))
    experience = exp_res.scalars().all()

    # Truthful completeness calculation
    checks = [
        bool(profile and profile.headline),
        bool(profile and profile.summary),
        bool(profile and profile.preferred_role),
        bool(profile and (profile.phone or profile.github_url)),
        len(education) > 0,
        len(projects) > 0,
        len(skills) > 0,
        len(experience) > 0,
    ]
    completeness = round((sum(1 for c in checks if c) / len(checks)) * 100)

    # Saved jobs count
    saved_count_res = await db.execute(
        select(func.count(SavedJob.id)).where(SavedJob.user_id == current_user.id, SavedJob.status == "saved")
    )
    saved_jobs_count = saved_count_res.scalar() or 0

    # Applications counts
    active_apps_res = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.stage.in_(["Applied", "Assessment", "Interview"])
        )
    )
    active_apps_count = active_apps_res.scalar() or 0

    total_apps_res = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == current_user.id)
    )
    total_apps_count = total_apps_res.scalar() or 0

    # Recent documents
    docs_count_res = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    documents_count = docs_count_res.scalar() or 0

    # Career Plan Progress
    plan_res = await db.execute(
        select(CareerPlan).where(CareerPlan.user_id == current_user.id, CareerPlan.status == "active").order_by(CareerPlan.created_at.desc())
    )
    active_plan = plan_res.scalar_one_or_none()
    
    plan_data = None
    next_task_data = None
    if active_plan:
        tasks_res = await db.execute(
            select(CareerPlanTask).where(CareerPlanTask.plan_id == active_plan.id).order_by(CareerPlanTask.day_number.asc())
        )
        tasks = tasks_res.scalars().all()
        completed_tasks = sum(1 for t in tasks if t.status == "completed")
        plan_progress = round((completed_tasks / max(1, len(tasks))) * 100) if tasks else 0
        
        # Next pending task
        pending_tasks = [t for t in tasks if t.status == "pending"]
        if pending_tasks:
            nt = pending_tasks[0]
            next_task_data = {
                "id": nt.id,
                "title": nt.title,
                "stage": nt.stage,
                "day_number": nt.day_number,
                "due_date": nt.due_date,
                "priority": nt.priority
            }

        plan_data = {
            "id": active_plan.id,
            "target_role": active_plan.target_role,
            "total_tasks": len(tasks),
            "completed_tasks": completed_tasks,
            "progress_percentage": plan_progress
        }

    # Recent Audit Activity
    audit_res = await db.execute(
        select(AuditEvent).where(AuditEvent.user_id == current_user.id).order_by(AuditEvent.created_at.desc()).limit(6)
    )
    recent_events = []
    for a in audit_res.scalars().all():
        try:
            d = json.loads(a.details_json) if a.details_json else {}
        except Exception:
            d = {}
        recent_events.append({
            "id": a.id,
            "event_type": a.event_type,
            "details": d,
            "created_at": a.created_at.isoformat() if a.created_at else None
        })

    # Recommended Jobs with Match Score
    cand_skills_data = [{"canonical_name": s.canonical_name, "proficiency_level": s.proficiency_level, "verified_status": s.verified_status} for s in skills]
    cand_projects_data = [{"title": p.title, "skills_used": p.skills_used} for p in projects]

    jobs_res = await db.execute(select(JobListing).where(JobListing.is_active == True).limit(5))
    recommended_jobs = []
    for j in jobs_res.scalars().all():
        req_sk = json.loads(j.required_skills) if j.required_skills else []
        pref_sk = json.loads(j.preferred_skills) if j.preferred_skills else []
        
        match_info = compute_job_match(
            candidate_skills=cand_skills_data,
            candidate_projects=cand_projects_data,
            candidate_experience=[],
            required_skills=req_sk,
            preferred_skills=pref_sk,
            work_arrangement=j.work_arrangement or "remote",
            candidate_arrangement_pref=profile.work_arrangement if profile else "remote"
        )
        recommended_jobs.append({
            "id": j.id,
            "title": j.title,
            "employer": j.employer,
            "location": j.location,
            "work_arrangement": j.work_arrangement,
            "salary_text": j.salary_text,
            "match_score": match_info["match_score"],
            "summary": match_info["explanation"]["summary"],
            "matched_skills": [m["skill"] for m in match_info["explanation"]["matched_required"][:3]]
        })

    recommended_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    # Next recommended action
    if documents_count == 0:
        next_action = "Upload your resume to the Document Scanner to extract verified skill and project evidence."
    elif not active_plan:
        next_action = "Generate your adaptive 30-day career plan to address identified skill gaps."
    elif next_task_data:
        next_action = f"Complete current career plan task: '{next_task_data['title']}'."
    else:
        next_action = "Apply to high-match opportunities and track them in your Application Pipeline."

    return {
        "candidate": {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "preferred_role": profile.preferred_role if profile else "Software Developer"
        },
        "stats": {
            "profile_completeness": completeness,
            "saved_jobs_count": saved_jobs_count,
            "active_applications_count": active_apps_count,
            "total_applications_count": total_apps_count,
            "documents_count": documents_count,
            "verified_skills_count": sum(1 for s in skills if s.verified_status in ["project_verified", "document_extracted"]),
            "projects_count": len(projects)
        },
        "next_suggested_action": next_action,
        "career_plan": plan_data,
        "next_task": next_task_data,
        "recommended_opportunities": recommended_jobs[:3],
        "recent_activity": recent_events
    }
