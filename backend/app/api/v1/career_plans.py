import json
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile, CandidateSkill
from backend.app.models.job import JobListing
from backend.app.models.career_plan import CareerPlan, CareerPlanTask
from backend.app.api.deps import get_current_user
from backend.app.services.skill_gap_service import analyze_skill_gaps
from backend.app.services.career_plan_service import generate_30_day_plan_tasks
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/career-plans", tags=["30-Day Adaptive Career Plan"])

class GeneratePlanRequest(BaseModel):
    target_role: str
    target_job_id: Optional[str] = None

class UpdateTaskRequest(BaseModel):
    status: str  # pending, in_progress, completed, skipped
    skip_reason: Optional[str] = None
    completion_evidence: Optional[str] = None

class CreateCustomTaskRequest(BaseModel):
    stage: str
    day_number: int
    title: str
    description: str
    linked_skill: Optional[str] = ""
    priority: Optional[str] = "Medium"
    duration_hours: Optional[int] = 2
    due_date: Optional[str] = ""

@router.get("/current")
async def get_current_career_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    plan_res = await db.execute(
        select(CareerPlan).where(CareerPlan.user_id == current_user.id, CareerPlan.status == "active").order_by(CareerPlan.created_at.desc())
    )
    plan = plan_res.scalar_one_or_none()
    if not plan:
        return {"plan": None, "tasks": [], "message": "No active career plan found. Generate one to begin."}

    tasks_res = await db.execute(
        select(CareerPlanTask).where(CareerPlanTask.plan_id == plan.id).order_by(CareerPlanTask.day_number.asc())
    )
    tasks = tasks_res.scalars().all()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    progress_percentage = round((completed_tasks / max(1, total_tasks)) * 100) if total_tasks else 0

    return {
        "plan": {
            "id": plan.id,
            "target_role": plan.target_role,
            "target_job_id": plan.target_job_id,
            "duration_days": plan.duration_days,
            "current_day": plan.current_day,
            "status": plan.status,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_percentage": progress_percentage
        },
        "tasks": [
            {
                "id": t.id,
                "stage": t.stage,
                "day_number": t.day_number,
                "title": t.title,
                "description": t.description,
                "linked_skill": t.linked_skill,
                "priority": t.priority,
                "duration_hours": t.duration_hours,
                "status": t.status,
                "skip_reason": t.skip_reason,
                "completion_evidence": t.completion_evidence,
                "due_date": t.due_date,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            } for t in tasks
        ]
    }

@router.post("/generate")
async def generate_career_plan(
    req: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    
    cand_skills = []
    if profile:
        skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
        cand_skills = [
            {"canonical_name": s.canonical_name, "proficiency_level": s.proficiency_level, "verified_status": s.verified_status}
            for s in skills_res.scalars().all()
        ]

    # Target job skills
    job_req_skills = ["Python", "React", "SQL", "Docker", "FastAPI"]
    job_pref_skills = ["Kubernetes", "TypeScript", "CI/CD"]
    
    if req.target_job_id:
        j_res = await db.execute(select(JobListing).where(JobListing.id == req.target_job_id))
        job = j_res.scalar_one_or_none()
        if job:
            if job.required_skills:
                job_req_skills = json.loads(job.required_skills)
            if job.preferred_skills:
                job_pref_skills = json.loads(job.preferred_skills)

    # Analyze gaps
    gap_analysis = analyze_skill_gaps(cand_skills, job_req_skills, job_pref_skills)

    # Deactivate any previous active plan
    prev_plans = await db.execute(select(CareerPlan).where(CareerPlan.user_id == current_user.id, CareerPlan.status == "active"))
    for p in prev_plans.scalars().all():
        p.status = "archived"

    # Create new plan
    new_plan = CareerPlan(
        user_id=current_user.id,
        target_role=req.target_role,
        target_job_id=req.target_job_id,
        duration_days=30,
        current_day=1,
        status="active"
    )
    db.add(new_plan)
    await db.flush()

    # Generate tasks across 4 stages
    tasks_data = generate_30_day_plan_tasks(
        target_role=req.target_role,
        skill_gaps=gap_analysis["skill_gaps"]
    )

    for td in tasks_data:
        task = CareerPlanTask(
            plan_id=new_plan.id,
            stage=td["stage"],
            day_number=td["day_number"],
            title=td["title"],
            description=td["description"],
            linked_skill=td["linked_skill"],
            priority=td["priority"],
            duration_hours=td["duration_hours"],
            due_date=td["due_date"],
            status="pending"
        )
        db.add(task)

    await db.commit()
    await db.refresh(new_plan)

    await log_audit_event(db, current_user.id, "career_plan_generated", {
        "plan_id": new_plan.id,
        "target_role": req.target_role,
        "gaps_count": len(gap_analysis["skill_gaps"])
    })

    return {
        "message": "30-day adaptive career plan generated successfully",
        "plan_id": new_plan.id,
        "gap_analysis": gap_analysis
    }

@router.put("/tasks/{task_id}")
async def update_plan_task(
    task_id: str,
    req: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task_res = await db.execute(select(CareerPlanTask).where(CareerPlanTask.id == task_id))
    task = task_res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = req.status
    if req.status == "completed":
        task.completed_at = datetime.now(timezone.utc)
        if req.completion_evidence:
            task.completion_evidence = req.completion_evidence
    elif req.status == "skipped":
        task.skip_reason = req.skip_reason or "Skipped by candidate"

    await db.commit()
    await log_audit_event(db, current_user.id, "career_task_updated", {"task_id": task_id, "status": req.status})
    return {"message": "Task updated successfully"}

@router.post("/tasks")
async def add_custom_task(
    req: CreateCustomTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    plan_res = await db.execute(select(CareerPlan).where(CareerPlan.user_id == current_user.id, CareerPlan.status == "active"))
    plan = plan_res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=400, detail="No active career plan found. Create one first.")

    task = CareerPlanTask(
        plan_id=plan.id,
        stage=req.stage,
        day_number=req.day_number,
        title=req.title,
        description=req.description,
        linked_skill=req.linked_skill or "",
        priority=req.priority or "Medium",
        duration_hours=req.duration_hours or 2,
        due_date=req.due_date or f"Day {req.day_number}",
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"message": "Custom task added", "id": task.id}
